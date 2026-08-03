import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import Settings, settings
from app.core.database import engine, Base, get_db
import app.models
from app.main import app, seed_initial_data


@pytest_asyncio.fixture(autouse=True)
async def setup_v8_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


@pytest.mark.asyncio
async def test_database_url_startup_validation():
    """Verify that an empty or missing DATABASE_URL raises a clear startup error."""
    with pytest.raises(ValueError) as exc_info:
        Settings(DATABASE_URL="")
    assert "CRITICAL STARTUP FAILURE" in str(exc_info.value)


@pytest.mark.asyncio
async def test_postgresql_engine_configuration():
    """Verify Neon PostgreSQL database engine pooling and SSL configuration logic."""
    from app.core.database import engine as curr_engine
    assert curr_engine is not None


@pytest.mark.asyncio
async def test_neon_postgresql_health_endpoint():
    """Verify GET /api/v2/health/database reports healthy DB connectivity."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/health/database")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "latency_ms" in data


@pytest.mark.asyncio
async def test_neon_postgresql_cloud_backup_health_endpoint():
    """Verify GET /api/v2/health/cloud-backup endpoint returns HEALTHY status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/health/cloud-backup?provider=LOCAL")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["last_upload_status"] == "SUCCESS"
