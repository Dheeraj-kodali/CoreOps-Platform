import os
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
from app.models.user import User
from app.models.purpose import Purpose
from app.core.security import get_password_hash
from sqlalchemy.future import select


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_admin_login_logout_session():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data

        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Profile fetch
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        user_info = me_res.json()
        assert user_info["username"] == "admin"

        # Logout & Session Revocation
        logout_res = await ac.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 200

        # Verify revoked token returns 401
        revoked_me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert revoked_me_res.status_code == 401


@pytest.mark.asyncio
async def test_forgot_and_reset_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        forgot_res = await ac.post("/api/v1/auth/forgot-password", json={"username_or_email": "admin"})
        assert forgot_res.status_code == 200
        data = forgot_res.json()
        assert "reset_token" in data

        reset_token = data["reset_token"]
        reset_res = await ac.post(
            "/api/v1/auth/reset-password",
            json={"reset_token": reset_token, "new_password": "NewSecretPass@123"}
        )
        assert reset_res.status_code == 200

        # Login with new password
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "NewSecretPass@123"}
        )
        assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_visitor_registration_and_search():
    # Fetch valid seeded purpose ID
    async with AsyncSessionLocal() as session:
        p_res = await session.execute(select(Purpose))
        purpose = p_res.scalars().first()
        purpose_id = purpose.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        access_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        visitor_payload = {
            "visitor_uuid": "11111111-2222-3333-4444-555555555555",
            "name": "Anjaneyulu",
            "phone_number": "+919876543210",
            "gender": "MALE",
            "age": 42,
            "persons_count": 4,
            "purpose_id": purpose_id,
            "temple_service": "Special Darshan",
            "visitor_date": "2026-07-26",
            "visitor_time": "10:30:00",
            "notes": "Testing backend API registration"
        }

        create_res = await ac.post("/api/v1/visitors/", json=visitor_payload, headers=headers)
        assert create_res.status_code == 201
        created_visitor = create_res.json()
        assert created_visitor["name"] == "Anjaneyulu"

        # List visitors
        list_res = await ac.get("/api/v1/visitors/?search=Anjaneyulu", headers=headers)
        assert list_res.status_code == 200
        assert list_res.json()["total"] >= 1
