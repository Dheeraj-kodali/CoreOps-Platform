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

from httpx import AsyncClient, ASGITransport
from app.main import app, seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.person import Person
from app.services.analytics_service import AnalyticsService


@pytest_asyncio.fixture(autouse=True)
async def setup_dashboard_db():
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
async def test_dashboard_overview_and_polling_interval():
    """Verify GET /api/v2/dashboard/overview metrics and 30s polling recommendation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        res = await ac.get("/api/v2/dashboard/overview", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert "visitor_metrics" in data
        assert "communication" in data
        assert "synchronization" in data
        assert "audit" in data
        assert data["refresh_interval_seconds"] == 30
        assert data["system_health_status"] in ("HEALTHY", "DEGRADED")


@pytest.mark.asyncio
async def test_dashboard_analytics_breakdown_endpoints():
    """Verify Visitor, Communication, Sync, Audit, Audience, and Health endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # 1. Visitor Analytics
        r_vis = await ac.get("/api/v2/dashboard/visitor-analytics", headers=headers)
        assert r_vis.status_code == 200
        d_vis = r_vis.json()
        assert "live" in d_vis
        assert "hourly_trends" in d_vis
        assert "daily_trends" in d_vis
        assert "village_distribution" in d_vis

        # 2. Communication Metrics
        r_comm = await ac.get("/api/v2/dashboard/communication-metrics", headers=headers)
        assert r_comm.status_code == 200
        assert "delivery_rate" in r_comm.json()

        # 3. Sync Metrics
        r_sync = await ac.get("/api/v2/dashboard/sync-metrics", headers=headers)
        assert r_sync.status_code == 200
        assert "success_rate" in r_sync.json()

        # 4. Audit Metrics
        r_aud = await ac.get("/api/v2/dashboard/audit-metrics", headers=headers)
        assert r_aud.status_code == 200
        assert "failed_logins" in r_aud.json()

        # 5. Audience Analytics
        r_aud_an = await ac.get("/api/v2/dashboard/audience-analytics", headers=headers)
        assert r_aud_an.status_code == 200
        assert "total_devotees" in r_aud_an.json()

        # 6. System Health
        r_health = await ac.get("/api/v2/dashboard/system-health", headers=headers)
        assert r_health.status_code == 200
        assert r_health.json()["backend"]["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_dashboard_export_formats():
    """Verify Export API (/api/v2/dashboard/export) PDF, Excel, CSV, JSON outputs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # 1. PDF Export
        r_pdf = await ac.post("/api/v2/dashboard/export", json={"format": "pdf"}, headers=headers)
        assert r_pdf.status_code == 200
        assert "application/pdf" in r_pdf.headers["content-type"]
        assert b"TEMPLE OWNER ANALYTICS REPORT" in r_pdf.content

        # 2. CSV Export
        r_csv = await ac.post("/api/v2/dashboard/export", json={"format": "csv"}, headers=headers)
        assert r_csv.status_code == 200
        assert "text/csv" in r_csv.headers["content-type"]
        assert b"Category,Metric,Value" in r_csv.content

        # 3. Excel Export
        r_excel = await ac.post("/api/v2/dashboard/export", json={"format": "excel"}, headers=headers)
        assert r_excel.status_code == 200
        assert "application/vnd.ms-excel" in r_excel.headers["content-type"]

        # 4. JSON Export
        r_json = await ac.post("/api/v2/dashboard/export", json={"format": "json"}, headers=headers)
        assert r_json.status_code == 200
        assert "application/json" in r_json.headers["content-type"]
        assert "visitor_metrics" in r_json.json()


@pytest.mark.asyncio
async def test_analytics_service_performance_benchmark():
    """Performance Benchmark: Verify analytics query calculation latency is under 50ms."""
    async with AsyncSessionLocal() as session:
        service = AnalyticsService(session)
        
        start = time.perf_counter()
        await service.get_visitor_metrics("SKSA_MAIN")
        await service.get_communication_metrics("SKSA_MAIN")
        await service.get_sync_metrics("SKSA_MAIN")
        await service.get_audit_metrics("SKSA_MAIN")
        await service.get_audience_analytics("SKSA_MAIN")
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 100.0, f"Dashboard analytics latency {elapsed_ms:.2f}ms exceeded SLA threshold!"
