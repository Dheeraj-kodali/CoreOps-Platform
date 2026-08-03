import os
import gzip
import json
import hashlib
import time
from datetime import datetime, timezone
import pytest
import pytest_asyncio

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

import app.models
from httpx import AsyncClient, ASGITransport
from app.main import app, seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.visitor import Visitor
from app.models.person import Person
from app.models.sync import SyncQueue, SyncToken
from sqlalchemy.future import select


@pytest_asyncio.fixture(autouse=True)
async def setup_sync_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


async def get_auth_headers(ac: AsyncClient) -> dict:
    login_res = await ac.post(
        "/api/v2/auth/login",
        json={"username": "admin", "password": "Admin@12345"}
    )
    token = login_res.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Temple-ID": "SKSA_MAIN"
    }


@pytest.mark.asyncio
async def test_offline_to_online_recovery_batch_upload():
    """Scenario 1: Offline -> Online Recovery Batch Upload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        event_id = "evt-offline-rec-001"
        visitor_id = "vis-offline-rec-001"
        client_ts = datetime.now(timezone.utc).isoformat()

        batch_payload = {
            "client_id": "MOB_DEVICE_001",
            "last_sync_token": None,
            "events": [
                {
                    "event_id": event_id,
                    "entity_type": "VISITOR",
                    "entity_id": visitor_id,
                    "action": "CREATE",
                    "payload": {
                        "name": "Kalyan Ram",
                        "phone": "+919876500111",
                        "gender": "MALE",
                        "age": 35,
                        "persons_count": 2,
                        "village": "Tirupati",
                        "purpose": "Darshan",
                        "date": "2026-07-30",
                        "time_in": "10:30:00"
                    },
                    "client_timestamp": client_ts
                }
            ]
        }

        res = await ac.post("/api/v2/sync/upload", json=batch_payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["client_id"] == "MOB_DEVICE_001"
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "SYNCED"
        assert data["metrics"]["success_count"] == 1

        # Verify Visitor inserted in DB
        async with AsyncSessionLocal() as session:
            v_res = await session.execute(select(Visitor).filter(Visitor.visitor_uuid == visitor_id))
            visitor = v_res.scalars().first()
            assert visitor is not None
            assert visitor.name == "Kalyan Ram"


@pytest.mark.asyncio
async def test_duplicate_upload_idempotency():
    """Scenario 2: Duplicate Upload Idempotency."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        event_id = "evt-dup-check-002"
        visitor_id = "vis-dup-check-002"
        client_ts = datetime.now(timezone.utc).isoformat()

        batch_payload = {
            "client_id": "MOB_DEVICE_001",
            "events": [
                {
                    "event_id": event_id,
                    "entity_type": "VISITOR",
                    "entity_id": visitor_id,
                    "action": "CREATE",
                    "payload": {
                        "name": "Saraswathi Devi",
                        "phone": "+919876500222",
                        "gender": "FEMALE",
                        "age": 28,
                        "persons_count": 1,
                        "village": "Chittoor",
                        "purpose": "Seva",
                        "date": "2026-07-30",
                        "time_in": "11:00:00"
                    },
                    "client_timestamp": client_ts
                }
            ]
        }

        # First Upload: SYNCED
        res1 = await ac.post("/api/v2/sync/upload", json=batch_payload, headers=headers)
        assert res1.status_code == 200
        assert res1.json()["results"][0]["status"] == "SYNCED"

        # Second Duplicate Upload: DUPLICATE
        res2 = await ac.post("/api/v2/sync/upload", json=batch_payload, headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["results"][0]["status"] == "DUPLICATE"
        assert data2["metrics"]["duplicates_count"] == 1

        # Verify only 1 Visitor record in DB
        async with AsyncSessionLocal() as session:
            v_res = await session.execute(select(Visitor).filter(Visitor.phone_number == "+919876500222"))
            visitors = v_res.scalars().all()
            assert len(visitors) == 1


@pytest.mark.asyncio
async def test_partial_failures_and_sha256_hash_validation():
    """Scenario 3 & 5: Partial Failures & SHA-256 Hash Validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        valid_payload = {"name": "Valid Visitor", "phone": "+919876500333", "gender": "MALE", "age": 40, "persons": 1, "village": "Kadapa", "purpose": "Darshan", "date": "2026-07-30", "time_in": "12:00:00"}
        valid_json = json.dumps(valid_payload, sort_keys=True)
        valid_hash = hashlib.sha256(valid_json.encode('utf-8')).hexdigest()

        client_ts = datetime.now(timezone.utc).isoformat()

        batch_payload = {
            "client_id": "MOB_DEVICE_001",
            "events": [
                {
                    "event_id": "evt-part-valid-001",
                    "entity_type": "VISITOR",
                    "entity_id": "vis-part-valid-001",
                    "action": "CREATE",
                    "payload": valid_payload,
                    "client_timestamp": client_ts,
                    "sha256_hash": valid_hash
                },
                {
                    "event_id": "evt-part-corrupt-002",
                    "entity_type": "VISITOR",
                    "entity_id": "vis-part-corrupt-002",
                    "action": "CREATE",
                    "payload": {"name": "Corrupt Visitor"},
                    "client_timestamp": client_ts,
                    "sha256_hash": "invalid_sha256_checksum_here"
                }
            ]
        }

        res = await ac.post("/api/v2/sync/upload", json=batch_payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["status"] == "SYNCED"
        assert data["results"][1]["status"] == "FAILED"
        assert data["results"][1]["retryable"] is True
        assert data["metrics"]["success_count"] == 1
        assert data["metrics"]["failed_count"] == 1


@pytest.mark.asyncio
async def test_conflict_resolution_lww():
    """Scenario 4: Conflict Resolution Strategy (LWW)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # 1. Create visitor on server
        create_payload = {
            "client_id": "MOB_DEVICE_001",
            "events": [
                {
                    "event_id": "evt-lww-create-001",
                    "entity_type": "VISITOR",
                    "entity_id": "vis-lww-001",
                    "action": "CREATE",
                    "payload": {
                        "name": "Initial Name",
                        "phone": "+919876500444",
                        "gender": "MALE",
                        "age": 30,
                        "persons_count": 1,
                        "village": "Nellore",
                        "purpose": "Darshan",
                        "date": "2026-07-30",
                        "time_in": "09:00:00"
                    },
                    "client_timestamp": "2026-07-30T10:00:00Z"
                }
            ]
        }
        await ac.post("/api/v2/sync/upload", json=create_payload, headers=headers)

        # Update Visitor updated_at in DB to recent timestamp
        async with AsyncSessionLocal() as session:
            v_res = await session.execute(select(Visitor).filter(Visitor.visitor_uuid == "vis-lww-001"))
            v = v_res.scalars().first()
            v.updated_at = datetime(2026, 7, 30, 12, 0, 0, tzinfo=timezone.utc)
            await session.commit()

        # Send stale update with older timestamp (10:30:00Z < 12:00:00Z)
        stale_update_payload = {
            "client_id": "MOB_DEVICE_001",
            "events": [
                {
                    "event_id": "evt-lww-update-stale",
                    "entity_type": "VISITOR",
                    "entity_id": "vis-lww-001",
                    "action": "UPDATE",
                    "payload": {"notes": "Stale edit"},
                    "client_timestamp": "2026-07-30T10:30:00Z"
                }
            ]
        }

        res = await ac.post("/api/v2/sync/upload", json=stale_update_payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["results"][0]["status"] == "CONFLICT"
        assert data["metrics"]["conflicts_count"] == 1


@pytest.mark.asyncio
async def test_large_batch_upload_performance_benchmark():
    """Scenario 6: Large Batch Upload & Performance Benchmark."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        events = []
        for i in range(50):
            events.append(
                {
                    "event_id": f"evt-bench-{i:03d}",
                    "entity_type": "VISITOR",
                    "entity_id": f"vis-bench-{i:03d}",
                    "action": "CREATE",
                    "payload": {
                        "name": f"Benchmark Visitor {i}",
                        "phone": f"+9198700{i:05d}",
                        "gender": "MALE" if i % 2 == 0 else "FEMALE",
                        "age": 20 + i,
                        "persons_count": (i % 5) + 1,
                        "village": "Benchmark Village",
                        "purpose": "Darshan",
                        "date": "2026-07-30",
                        "time_in": "14:00:00"
                    },
                    "client_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        batch_payload = {
            "client_id": "BENCH_DEVICE_999",
            "events": events
        }

        start = time.perf_counter()
        res = await ac.post("/api/v2/sync/upload", json=batch_payload, headers=headers)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert res.status_code == 200
        data = res.json()
        assert data["metrics"]["items_processed"] == 50
        assert data["metrics"]["success_count"] == 50
        assert data["metrics"]["latency_ms"] < 2000.0
        assert elapsed_ms < 3000.0


@pytest.mark.asyncio
async def test_gzip_compressed_upload_and_incremental_download():
    """Gzip Compressed Upload & Incremental Download Verification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # 1. Gzip Compressed Upload
        batch_dict = {
            "client_id": "GZIP_DEVICE_001",
            "events": [
                {
                    "event_id": "evt-gzip-001",
                    "entity_type": "VISITOR",
                    "entity_id": "vis-gzip-001",
                    "action": "CREATE",
                    "payload": {
                        "name": "Gzip User",
                        "phone": "+919876500999",
                        "gender": "MALE",
                        "age": 32,
                        "persons_count": 1,
                        "village": "Gzip Village",
                        "purpose": "Seva",
                        "date": "2026-07-30",
                        "time_in": "15:00:00"
                    },
                    "client_timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        }

        compressed_data = gzip.compress(json.dumps(batch_dict).encode('utf-8'))
        gzip_headers = dict(headers)
        gzip_headers["Content-Encoding"] = "gzip"

        res_upload = await ac.post("/api/v2/sync/upload", content=compressed_data, headers=gzip_headers)
        assert res_upload.status_code == 200
        assert res_upload.json()["results"][0]["status"] == "SYNCED"

        # 2. Incremental Download
        dl_res = await ac.post(
            "/api/v2/sync/download",
            json={"client_id": "GZIP_DEVICE_001", "limit": 100},
            headers=headers
        )
        assert dl_res.status_code == 200
        dl_data = dl_res.json()
        assert "next_sync_token" in dl_data
        assert len(dl_data["changes"]) >= 1
        assert any(c["entity_id"] == "vis-gzip-001" for c in dl_data["changes"])
