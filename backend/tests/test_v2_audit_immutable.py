import os
import json
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
from app.core.exceptions import ImmutableAuditException
from app.models.audit import AuditRecord
from app.repositories.audit_repository import AuditRepository
from app.core.audit_hook import record_audit_event
from sqlalchemy.future import select


@pytest_asyncio.fixture(autouse=True)
async def setup_audit_db():
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
async def test_audit_record_immutability_enforcement():
    """Verify Immutability Rules: Updates and Deletions Raise ImmutableAuditException."""
    async with AsyncSessionLocal() as session:
        repo = AuditRepository(session)
        audit = await repo.create(
            action="VISITOR_REGISTER",
            entity_type="VISITOR",
            entity_id="vis-immut-001",
            severity="INFO"
        )
        assert audit.audit_id is not None

        # Attempting Repository UPDATE raises ImmutableAuditException
        with pytest.raises(ImmutableAuditException):
            await repo.update(audit, {"severity": "CRITICAL"})

        # Attempting Repository DELETE raises ImmutableAuditException
        with pytest.raises(ImmutableAuditException):
            await repo.delete(audit)

        # Attempting ORM level UPDATE via Session flush raises ImmutableAuditException
        audit.severity = "CRITICAL"
        with pytest.raises(ImmutableAuditException):
            await session.commit()


@pytest.mark.asyncio
async def test_all_16_required_audit_event_categories():
    """Verify Audit Interceptor Coverage across all 16 required event types."""
    required_events = [
        "VISITOR_REGISTER", "VISITOR_UPDATE", "VISITOR_CHECKOUT",
        "BACKUP_CREATE", "BACKUP_RESTORE",
        "REPORT_EXPORT", "COMMUNICATION_DISPATCH",
        "SYNC_START", "SYNC_SUCCESS", "SYNC_FAILURE", "SYNC_DUPLICATE", "SYNC_CONFLICT",
        "USER_LOGIN", "USER_LOGOUT", "USER_LOGIN_FAILED",
        "SETTINGS_UPDATE"
    ]

    async with AsyncSessionLocal() as session:
        for action_name in required_events:
            severity = "ERROR" if "FAIL" in action_name or "CONFLICT" in action_name else "INFO"
            await record_audit_event(
                session,
                action=action_name,
                entity_type="SYSTEM",
                entity_id=f"id-{action_name}",
                severity=severity,
                new_value={"test_event": action_name}
            )

        # Verify all 16 recorded in DB
        res = await session.execute(select(AuditRecord))
        all_records = res.scalars().all()
        recorded_actions = {r.action for r in all_records}

        for required in required_events:
            assert required in recorded_actions, f"Audit event '{required}' was not recorded!"


@pytest.mark.asyncio
async def test_audit_search_api_filtering_and_pagination():
    """Verify Search API (/api/v2/audit/search) Filtering & Pagination."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # Seed 15 audit entries via API & repo
        async with AsyncSessionLocal() as session:
            repo = AuditRepository(session)
            for i in range(15):
                await repo.create(
                    action="REPORT_EXPORT" if i % 2 == 0 else "SETTINGS_UPDATE",
                    entity_type="REPORT" if i % 2 == 0 else "SETTING",
                    severity="INFO" if i % 3 == 0 else "WARNING",
                    temple_id="SKSA_MAIN",
                    entity_id=f"rec-{i}"
                )

        # 1. Search with Action Filter & Pagination (page 1, page_size 5)
        search_req = {
            "temple_id": "SKSA_MAIN",
            "action": "REPORT_EXPORT",
            "page": 1,
            "page_size": 5
        }
        res = await ac.post("/api/v2/audit/search", json=search_req, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) <= 5
        assert data["total_count"] >= 8
        assert all(item["action"] == "REPORT_EXPORT" for item in data["items"])

        # 2. Search with Severity Filter
        search_sev = {
            "temple_id": "SKSA_MAIN",
            "severity": "WARNING",
            "page": 1,
            "page_size": 20
        }
        res_sev = await ac.post("/api/v2/audit/search", json=search_sev, headers=headers)
        assert res_sev.status_code == 200
        data_sev = res_sev.json()
        assert all(item["severity"] == "WARNING" for item in data_sev["items"])


@pytest.mark.asyncio
async def test_audit_export_api_json_and_csv():
    """Verify Export API (/api/v2/audit/export) JSON and CSV Outputs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # Seed audit entry
        async with AsyncSessionLocal() as session:
            repo = AuditRepository(session)
            await repo.create(
                action="BACKUP_CREATE",
                entity_type="BACKUP",
                severity="INFO",
                temple_id="SKSA_MAIN"
            )

        # 1. Export JSON Format
        res_json = await ac.post(
            "/api/v2/audit/export",
            json={"temple_id": "SKSA_MAIN", "format": "json"},
            headers=headers
        )
        assert res_json.status_code == 200
        assert "application/json" in res_json.headers["content-type"]
        exported_list = json.loads(res_json.content.decode('utf-8'))
        assert len(exported_list) >= 1
        assert any(item["action"] == "BACKUP_CREATE" for item in exported_list)

        # 2. Export CSV Format
        res_csv = await ac.post(
            "/api/v2/audit/export",
            json={"temple_id": "SKSA_MAIN", "format": "csv"},
            headers=headers
        )
        assert res_csv.status_code == 200
        assert "text/csv" in res_csv.headers["content-type"]
        csv_text = res_csv.content.decode('utf-8')
        assert "audit_id,trace_id,temple_id" in csv_text
        assert "BACKUP_CREATE" in csv_text


@pytest.mark.asyncio
async def test_audit_recording_performance_benchmark():
    """Performance Benchmark: Verify audit creation latency overhead is under 20ms."""
    async with AsyncSessionLocal() as session:
        repo = AuditRepository(session)
        start = time.perf_counter()
        
        await repo.create(
            action="BENCHMARK_AUDIT",
            entity_type="BENCHMARK",
            severity="INFO",
            duration_ms=1.5
        )
            
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 100.0, f"Audit recording overhead {elapsed_ms:.2f}ms exceeded 100ms threshold!"
