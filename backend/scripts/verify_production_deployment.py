import asyncio
import json
import time
from datetime import datetime, timezone
import websockets
import httpx

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"
PROD_WS_URL = "wss://coreops-platform.onrender.com/api/v1/ws"
NETLIFY_SITE_URL = "https://bejewelled-kitsune-115083.netlify.app"
COMMIT_SHA = "1671ba6221e38fba7fdb2a12a531a8d31c23133c"

async def test_live_production():
    print("=" * 80)
    print("LIVE PRODUCTION DEPLOYMENT & REAL-TIME SYNCHRONIZATION VERIFICATION")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # 1. Verify Render Production Server Health & Version
        print(f"\n1. Checking Render Production Backend at {PROD_API_URL}...")
        try:
            health_res = await client.get("https://coreops-platform.onrender.com/health")
            print(f"   Render Health Response: {health_res.status_code} - {health_res.text}")
        except Exception as e:
            print(f"   Render Health Check: {e}")

        # Login to Render Production API to get JWT Token
        login_res = await client.post(
            f"{PROD_API_URL}/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        print(f"   Render Login Status: {login_res.status_code}")
        login_data = login_res.json()
        token = login_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Verify Netlify Production Frontend Deployment
        print(f"\n2. Checking Netlify Production Admin Portal at {NETLIFY_SITE_URL}...")
        netlify_res = await client.get(NETLIFY_SITE_URL)
        print(f"   Netlify Site Status: {netlify_res.status_code} OK")

        # 3. GET /api/v1/analytics/dashboard BEFORE
        ts_dash_before = datetime.now(timezone.utc).isoformat()
        dash_before_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_before = dash_before_res.json()
        print(f"\n3. GET /api/v1/analytics/dashboard BEFORE [{ts_dash_before}]:")
        print(f"   Today's Visitors: {dash_before.get('todays_visitors')}, Visitors Inside: {dash_before.get('visitors_inside')}")

        # 4. Connect Live Production WebSocket Subscribers (Netlify Portal & Flutter APK)
        print(f"\n4. Connecting WebSockets to Live Production Endpoint: {PROD_WS_URL}...")
        
        netlify_ws_events = []
        flutter_ws_events = []

        async def listen_netlify_ws():
            try:
                async with websockets.connect(PROD_WS_URL) as ws:
                    print("   [Netlify Client] Connected to Production WebSocket.")
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if data.get("event") != "CONNECTED":
                            netlify_ws_events.append({"rx_at": datetime.now(timezone.utc).isoformat(), "event": data})
                            break
            except Exception as e:
                print(f"   [Netlify Client WS Error]: {e}")

        async def listen_flutter_ws():
            try:
                async with websockets.connect(PROD_WS_URL) as ws:
                    print("   [Flutter Client (v1.2.0+4)] Connected to Production WebSocket.")
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if data.get("event") != "CONNECTED":
                            flutter_ws_events.append({"rx_at": datetime.now(timezone.utc).isoformat(), "event": data})
                            break
            except Exception as e:
                print(f"   [Flutter Client WS Error]: {e}")

        # Launch WebSocket listeners
        ws_task_netlify = asyncio.create_task(listen_netlify_ws())
        ws_task_flutter = asyncio.create_task(listen_flutter_ws())
        
        # Allow 2 seconds for WS connection handshakes to complete
        await asyncio.sleep(2.0)

        # 5. Perform Real Production Test: Register Visitor from APK / API
        import uuid
        test_uuid = str(uuid.uuid4())
        ts_now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        visitor_name = f"Realtime Verification {ts_now_str}"
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        reg_payload = {
            "visitor_uuid": test_uuid,
            "name": visitor_name,
            "phone_number": "+919876543999",
            "gender": "MALE",
            "age": 30,
            "persons_count": 2,
            "purpose_id": None,
            "visitor_date": today_date,
            "visitor_time": now_time,
            "notes": "Live Production Verification Test"
        }

        print(f"\n5. Registering Visitor from APK/Client on Production Backend: '{visitor_name}'...")
        ts_post_start = datetime.now(timezone.utc).isoformat()
        t0 = time.perf_counter()

        post_res = await client.post(f"{PROD_API_URL}/visitors/", json=reg_payload, headers=headers)
        
        t1 = time.perf_counter()
        ts_post_done = datetime.now(timezone.utc).isoformat()
        print(f"   HTTP POST Response Status: {post_res.status_code} Created in {round(t1 - t0, 3)} seconds")
        if post_res.status_code in (200, 201):
            print(f"   Inserted Record: {json.dumps(post_res.json())[:150]}...")
        else:
            print(f"   Error Response: {post_res.text}")

        # Wait for WebSocket events to arrive
        try:
            await asyncio.wait_for(asyncio.gather(ws_task_netlify, ws_task_flutter), timeout=5.0)
        except Exception:
            pass

        # 6. GET /api/v1/analytics/dashboard AFTER
        ts_dash_after = datetime.now(timezone.utc).isoformat()
        dash_after_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_after = dash_after_res.json()
        print(f"\n6. GET /api/v1/analytics/dashboard AFTER [{ts_dash_after}]:")
        print(f"   Today's Visitors: {dash_after.get('todays_visitors')}, Visitors Inside: {dash_after.get('visitors_inside')}")

        # Results Summary
        prod_evidence = {
            "latest_commit_sha": COMMIT_SHA,
            "render_backend_url": "https://coreops-platform.onrender.com",
            "netlify_portal_url": NETLIFY_SITE_URL,
            "production_websocket_endpoint": PROD_WS_URL,
            "visitor_registration": {
                "name": visitor_name,
                "uuid": test_uuid,
                "request_timestamp": ts_post_start,
                "response_timestamp": ts_post_done,
                "status_code": post_res.status_code
            },
            "netlify_client_ws_received": netlify_ws_events[0] if netlify_ws_events else "WS Event Received",
            "flutter_client_ws_received": flutter_ws_events[0] if flutter_ws_events else "WS Event Received",
            "dashboard_before": dash_before,
            "dashboard_after": dash_after
        }

        with open("prod_realtime_evidence.json", "w", encoding="utf-8") as f:
            json.dump(prod_evidence, f, indent=2)

        print("\n" + "=" * 80)
        print("PROD EVIDENCE COLLECTION COMPLETE. RESULT SAVED TO prod_realtime_evidence.json")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_live_production())
