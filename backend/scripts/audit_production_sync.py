import urllib.request
import json
import time
import uuid
import websockets
import asyncio
from datetime import datetime, timezone

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"
PROD_WS_URL = "wss://coreops-platform.onrender.com/api/v1/ws"

async def run_audit():
    print("Starting Live Production Audit...")
    
    # 1. Login to get token
    login_data = json.dumps({"username": "admin", "password": "Admin@12345"}).encode("utf-8")
    req = urllib.request.Request(f"{PROD_API_URL}/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    token = json.loads(res.read().decode("utf-8"))["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Get Dashboard BEFORE
    req_dash = urllib.request.Request(f"{PROD_API_URL}/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    dash_before = json.loads(urllib.request.urlopen(req_dash).read().decode("utf-8"))

    # 3. Connect WS listener
    ws_received = []
    async def listen_ws():
        try:
            async with websockets.connect(PROD_WS_URL) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("event") != "CONNECTED":
                        ws_received.append((datetime.now(timezone.utc).isoformat(), data))
                        break
        except Exception as e:
            ws_received.append((datetime.now(timezone.utc).isoformat(), {"error": str(e)}))

    ws_task = asyncio.create_task(listen_ws())
    await asyncio.sleep(1.5)

    # 4. Post Live Visitor with persons_count = 3
    test_uuid = str(uuid.uuid4())
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
    unique_phone = f"+91987{int(time.time()) % 10000000:07d}"

    payload = {
        "visitor_uuid": test_uuid,
        "name": "Audit Family Registration (3 people)",
        "phone_number": unique_phone,
        "gender": "FEMALE",
        "age": 28,
        "persons_count": 3,
        "purpose_id": None,
        "visitor_date": today_date,
        "visitor_time": now_time,
        "notes": "Single session with 3 family members for audit"
    }

    ts_post = datetime.now(timezone.utc).isoformat()
    req_post = urllib.request.Request(f"{PROD_API_URL}/visitors/", data=json.dumps(payload).encode("utf-8"), headers=headers)
    res_post = urllib.request.urlopen(req_post)
    post_data = json.loads(res_post.read().decode("utf-8"))
    ts_resp = datetime.now(timezone.utc).isoformat()

    try:
        await asyncio.wait_for(ws_task, timeout=5.0)
    except Exception:
        pass

    # 5. Get Dashboard AFTER
    req_dash_after = urllib.request.Request(f"{PROD_API_URL}/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    dash_after = json.loads(urllib.request.urlopen(req_dash_after).read().decode("utf-8"))

    # 6. Get Ledger TODAY
    req_ledger = urllib.request.Request(f"{PROD_API_URL}/visitors/ledgers/today", headers={"Authorization": f"Bearer {token}"})
    ledger_today = json.loads(urllib.request.urlopen(req_ledger).read().decode("utf-8"))

    audit_result = {
        "post_request_timestamp": ts_post,
        "post_response_timestamp": ts_resp,
        "post_request_payload": payload,
        "post_response_data": post_data,
        "dashboard_before": dash_before,
        "dashboard_after": dash_after,
        "ledger_today": ledger_today,
        "ws_received_event": ws_received[0] if ws_received else None
    }
    with open("production_audit_telemetry.json", "w", encoding="utf-8") as f:
        json.dump(audit_result, f, indent=2)

    print("AUDIT_SUCCESS: Saved telemetry to production_audit_telemetry.json")

if __name__ == "__main__":
    asyncio.run(run_audit())
