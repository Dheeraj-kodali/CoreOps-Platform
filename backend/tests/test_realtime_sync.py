import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

from sqlalchemy.future import select
from httpx import AsyncClient, ASGITransport
import app.models
from app.main import app, seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.websocket import websocket_manager
from app.models.user import User, Role, UserRole
from app.models.visitor import Visitor
from app.models.purpose import Purpose
from app.models.temple import Temple
from app.models.session import Session as UserSession
from app.core.security import get_password_hash, create_access_token


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()

    async with AsyncSessionLocal() as session:
        u_res = await session.execute(select(User).filter(User.username == "admin"))
        admin_user = u_res.scalars().first()

        jti = f"test_jti_{admin_user.id}"
        token, _ = create_access_token(subject=admin_user.id, jti=jti)
        app.state.test_token = token

        active_sess = UserSession(
            user_id=admin_user.id,
            token_jti=jti,
            refresh_token=f"ref_{jti}",
            is_revoked=False,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1)
        )
        session.add(active_sess)
        await session.commit()

    yield


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
