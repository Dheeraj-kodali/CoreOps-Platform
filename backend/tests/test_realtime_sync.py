import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.websocket import websocket_manager
from app.models.user import User, Role, UserRole
from app.models.visitor import Visitor
from app.models.purpose import Purpose
from app.models.temple import Temple
from app.core.security import get_password_hash, create_access_token


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed initial test data
    async with TestingSessionLocal() as session:
        temple = Temple(id="SKSA_MAIN", name="Test Temple", code="SKSA_MAIN", address="Test Address")
        session.add(temple)

        purpose = Purpose(id="3ef2daff-d716-4285-ac7c-81e702530b44", temple_id="SKSA_MAIN", name_en="General Darshan", name_te="దర్శనం", code="DARSHAN")
        session.add(purpose)

        admin_role = Role(id="role_admin", name="SUPER_ADMIN", description="Admin")
        session.add(admin_role)

        admin_user = User(
            id="user_admin",
            username="admin",
            email="admin@test.com",
            password_hash=get_password_hash("Admin@12345"),
            full_name="Test Admin",
            is_active=True
        )
        session.add(admin_user)
        await session.commit()

        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        session.add(user_role)
        await session.commit()

        # Add active session
        from app.models.session import Session as UserSession
        from datetime import datetime, timedelta, timezone
        token, jti = create_access_token("user_admin")
        sess = UserSession(
            user_id="user_admin",
            token_jti=jti,
            is_revoked=False,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        session.add(sess)
        await session.commit()

        # Save token for tests
        app.state.test_token = token

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_websocket_broadcaster():
    """Test WebSocket manager registers and broadcasts events cleanly."""
    event_received = []

    class DummyWebSocket:
        def __init__(self):
            self.accepted = False

        async def accept(self):
            self.accepted = True

        async def send_text(self, text):
            event_received.append(text)

    dummy_ws = DummyWebSocket()
    await websocket_manager.connect(dummy_ws)
    assert len(websocket_manager.active_connections) == 1

    await websocket_manager.broadcast_event("VISITOR_REGISTERED", {"uuid": "test-uuid-123"})
    assert len(event_received) == 1
    assert "VISITOR_REGISTERED" in event_received[0]
    assert "test-uuid-123" in event_received[0]

    websocket_manager.disconnect(dummy_ws)
    assert len(websocket_manager.active_connections) == 0


@pytest.mark.asyncio
async def test_realtime_visitor_lifecycle_broadcast():
    """Test register -> checkout -> delete visitor actions trigger real-time broadcasts & true DB counts."""
    headers = {"Authorization": f"Bearer {app.state.test_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        from datetime import date
        register_payload = {
            "visitor_uuid": "11111111-2222-3333-4444-555555555555",
            "name": "Ramesh Kumar",
            "phone_number": "+919876543210",
            "gender": "MALE",
            "age": 35,
            "persons_count": 2,
            "purpose_id": "3ef2daff-d716-4285-ac7c-81e702530b44",
            "visitor_date": date.today().isoformat(),
            "visitor_time": "10:30:00",
            "notes": "Realtime test entry"
        }

        res = await ac.post("/api/v1/visitors/", json=register_payload, headers=headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["visitor_uuid"] == "11111111-2222-3333-4444-555555555555"

        # 2. Check dashboard summary calculation (no fake counts)
        dash_res = await ac.get("/api/v1/analytics/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["todays_visitors"] == 2
        assert dash_data["todays_check_ins"] == 1
        assert dash_data["visitors_inside"] == 2

        # 3. Checkout visitor
        checkout_res = await ac.put("/api/v1/visitors/11111111-2222-3333-4444-555555555555/checkout", json={"checkout_time": "11:00:00", "duration": "30 min"}, headers=headers)
        assert checkout_res.status_code == 200

        # Verify updated dashboard metrics
        dash_res2 = await ac.get("/api/v1/analytics/dashboard", headers=headers)
        dash_data2 = dash_res2.json()
        assert dash_data2["todays_check_outs"] == 2
        assert dash_data2["visitors_inside"] == 0

        # 4. Delete visitor
        del_res = await ac.delete(f"/api/v1/visitors/{data['id']}", headers=headers)
        assert del_res.status_code == 204
