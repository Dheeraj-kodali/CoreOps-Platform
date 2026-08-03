import os
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
from app.core.rbac import user_has_permission, ROLE_OWNER, ROLE_VOLUNTEER, PERM_BROADCAST_CREATE, PERM_VISITOR_REGISTER
from app.core.audit_hook import record_audit_event
from app.models.audit import AuditLog
from app.models.person import Person
from app.models.sync import SyncToken
from sqlalchemy.future import select


@pytest_asyncio.fixture(autouse=True)
async def setup_v2_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


@pytest.mark.asyncio
async def test_api_v2_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["version"] == "v2.0"
    assert data["multi_tenant"] is True


@pytest.mark.asyncio
async def test_api_v2_auth_flow_login_refresh_me_logout():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login with valid admin credentials
        login_res = await ac.post(
            "/api/v2/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Temple-ID": "SKSA_MAIN"
        }

        # 2. Get me profile with RBAC permissions
        me_res = await ac.get("/api/v2/auth/me", headers=headers)
        assert me_res.status_code == 200
        profile = me_res.json()
        assert profile["username"] == "admin"
        assert profile["temple_id"] == "SKSA_MAIN"
        assert "SUPER_ADMIN" in profile["roles"]
        assert len(profile["permissions"]) > 0

        # 3. Refresh access token
        refresh_res = await ac.post("/api/v2/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_res.status_code == 200
        new_access_token = refresh_res.json()["access_token"]
        assert new_access_token is not None

        # 4. Logout session
        logout_res = await ac.post("/api/v2/auth/logout", headers=headers)
        assert logout_res.status_code == 200


@pytest.mark.asyncio
async def test_api_v2_auth_invalid_credentials():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v2/auth/login",
            json={"username": "admin", "password": "WrongPassword123"}
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_rbac_permission_matrix():
    assert user_has_permission([ROLE_OWNER], PERM_BROADCAST_CREATE) is True
    assert user_has_permission([ROLE_VOLUNTEER], PERM_BROADCAST_CREATE) is False
    assert user_has_permission([ROLE_VOLUNTEER], PERM_VISITOR_REGISTER) is True


@pytest.mark.asyncio
async def test_audit_hook_interceptor():
    async with AsyncSessionLocal() as session:
        audit = await record_audit_event(
            session,
            action="TEST_ACTION",
            resource="test_resource",
            user_id="usr-123",
            temple_id="SKSA_MAIN",
            role="OWNER",
            result="SUCCESS",
            reason="Step 2 Foundation Verification"
        )
        assert (getattr(audit, "audit_id", None) or getattr(audit, "id", None)) is not None

        # Query back audit record
        res = await session.execute(select(AuditLog).filter(AuditLog.action == "TEST_ACTION"))
        queried_audit = res.scalars().first()
        assert queried_audit is not None
        assert queried_audit.resource == "test_resource"


@pytest.mark.asyncio
async def test_db_schema_person_and_sync_tokens():
    async with AsyncSessionLocal() as session:
        person = Person(
            temple_id="SKSA_MAIN",
            name="Ramesh Kumar",
            phone="+919876543999",
            village="Kovur",
            first_visit="2026-07-30 10:00",
            last_visit="2026-07-30 10:00",
            total_visits=1
        )
        session.add(person)
        
        sync_token = SyncToken(
            temple_id="SKSA_MAIN",
            client_id="DEV_MOB_001",
            device_name="Temple Mobile Tablet",
            last_synced_token="vec_0001"
        )
        session.add(sync_token)
        await session.commit()

        # Query Person
        p_res = await session.execute(select(Person).filter(Person.phone == "+919876543999"))
        queried_person = p_res.scalars().first()
        assert queried_person is not None
        assert queried_person.name == "Ramesh Kumar"

        # Query SyncToken
        s_res = await session.execute(select(SyncToken).filter(SyncToken.client_id == "DEV_MOB_001"))
        queried_token = s_res.scalars().first()
        assert queried_token is not None
        assert queried_token.last_synced_token == "vec_0001"
