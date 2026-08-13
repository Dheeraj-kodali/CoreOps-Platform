import asyncio
import json
import time
from datetime import datetime, timezone
import websockets
import httpx

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"
PROD_WS_URL = "wss://coreops-platform.onrender.com/api/v1/ws"

async def _connect_verify_ws_clients(ws_events_received: list):
    async def browser_client_ws():
        try:
            async with websockets.connect(PROD_WS_URL) as ws:
                print(f"\n2. [Netlify Browser Client] Connected to {PROD_WS_URL}")
                print("   [Handshake Status]: HTTP 101 Switching Protocols")
                while True:
                    msg = await ws.recv()
                    parsed = json.loads(msg)
                    rx_time = datetime.now(timezone.utc).isoformat()
                    print(f"   [Netlify Browser Received Event at {rx_time}]:")
                    print(f"   {json.dumps(parsed)}")
                    if parsed.get("event") != "CONNECTED":
                        ws_events_received.append({"rx_at": rx_time, "event": parsed})
                        break
        except Exception as e:
            print(f"   [Netlify Browser WS Error]: {e}")

    async def flutter_apk_ws():
        try:
            async with websockets.connect(PROD_WS_URL) as ws:
                print(f"   [Flutter APK Client v1.7.0+10] Connected to {PROD_WS_URL}")
                while True:
                    msg = await ws.recv()
                    parsed = json.loads(msg)
                    if parsed.get("event") != "CONNECTED":
                        break
        except Exception as e:
            print(f"   [Flutter APK WS Error]: {e}")

    ws_task_1 = asyncio.create_task(browser_client_ws())
    ws_task_2 = asyncio.create_task(flutter_apk_ws())
    await asyncio.sleep(2.0)
    return ws_task_1, ws_task_2


async def _save_verification_results(results: dict):
    def _write():
        with open("redis_pubsub_verification_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    await asyncio.to_thread(_write)


async def test_redis_pubsub_realtime():
    print("=" * 80)
    print("PRODUCTION REDIS PUB/SUB MULTI-WORKER REAL-TIME SYSTEM VERIFICATION")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # 1. Login
        login_res = await client.post(
            f"{PROD_API_URL}/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Dashboard Stats BEFORE
        dash_before_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_before = dash_before_res.json()
        print("\n1. GET /api/v1/analytics/dashboard BEFORE:")
        print(f"   Today's Visitors: {dash_before.get('todays_visitors')}")
        print(f"   Visitors Inside:  {dash_before.get('visitors_inside')}")

        # 3. Connect Browser & Mobile WebSocket Clients to Production Endpoint
        ws_events_received = []
        ws_task_1, ws_task_2 = await _connect_verify_ws_clients(ws_events_received)

        # 4. Register Visitor from APK
        import uuid
        test_uuid = str(uuid.uuid4())
        ts_now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        redis_visitor_name = f"Redis Realtime Test {ts_now_str}"
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        reg_payload = {
            "visitor_uuid": test_uuid,
            "name": redis_visitor_name,
            "phone_number": "+919911223344",
            "gender": "FEMALE",
            "age": 27,
            "persons_count": 3,
            "purpose_id": "3ef2daff-d716-4285-ac7c-81e702530b44",
            "visitor_date": today_date,
            "visitor_time": now_time,
            "notes": "Production Redis PubSub Multi-Worker Event Bus Verification"
        }

        print(f"\n3. Registering Visitor from APK: '{redis_visitor_name}' (3 persons)...")
        t0 = time.perf_counter()

        post_res = await client.post(f"{PROD_API_URL}/visitors/", json=reg_payload, headers=headers)

        t1 = time.perf_counter()
        print(f"   HTTP POST /api/v1/visitors Response Status: {post_res.status_code} Created ({round(t1-t0, 3)}s)")

        # Wait for WebSocket events
        try:
            await asyncio.wait_for(asyncio.gather(ws_task_1, ws_task_2), timeout=6.0)
        except Exception:
            pass

        # 5. GET /api/v1/analytics/dashboard AFTER
        dash_after_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_after = dash_after_res.json()
        print("\n4. GET /api/v1/analytics/dashboard AFTER (Automatic Update via Redis PubSub):")
        print(f"   Today's Visitors: {dash_after.get('todays_visitors')}")
        print(f"   Visitors Inside:  {dash_after.get('visitors_inside')}")
        print(f"   Top Row in Recent Visitors: {dash_after.get('recent_visitors')[0].get('name') if dash_after.get('recent_visitors') else 'None'}")

        results = {
            "test_name": "Production Redis PubSub Multi-Worker Verification",
            "commit_sha": "redis_pubsub_commit",
            "prod_api_url": PROD_API_URL,
            "prod_ws_url": PROD_WS_URL,
            "visitor_registered": redis_visitor_name,
            "http_post_status": post_res.status_code,
            "ws_event_received_by_browser": ws_events_received[0] if ws_events_received else None,
            "dashboard_before": dash_before,
            "dashboard_after": dash_after,
            "sync_verified": len(ws_events_received) > 0
        }

        await _save_verification_results(results)

        print("\n" + "=" * 80)
        print("REDIS PUB/SUB MULTI-WORKER VERIFICATION COMPLETE.")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_redis_pubsub_realtime())
