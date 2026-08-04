import urllib.request
import json
import time
import uuid
import websockets
import asyncio
from datetime import datetime, timezone

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"
PROD_WS_URL = "wss://coreops-platform.onrender.com/api/v1/ws"

def safe_urlopen(req, retries=5, delay=5):
    for i in range(retries):
        try:
            return urllib.request.urlopen(req, timeout=15)
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay)

async def run_e2e_verification():
    print("=" * 80)
    print("STARTING E2E PRODUCTION VERIFICATION AFTER SYNC FIX")
    print("=" * 80)

    # 1. Login
    login_data = json.dumps({"username": "admin", "password": "Admin@12345"}).encode("utf-8")
    req = urllib.request.Request(f"{PROD_API_URL}/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    res = safe_urlopen(req)
    token = json.loads(res.read().decode("utf-8"))["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Get Dashboard BEFORE
    req_dash_b = urllib.request.Request(f"{PROD_API_URL}/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    dash_before = json.loads(safe_urlopen(req_dash_b).read().decode("utf-8"))
    print(f"Dashboard BEFORE registration: {dash_before}")

    # 3. Connect WebSocket listener
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

    # 4. Register new visitor with persons_count = 2
    test_uuid = str(uuid.uuid4())
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
    unique_phone = f"+91987{int(time.time()) % 10000000:07d}"

    payload = {
        "visitor_uuid": test_uuid,
        "name": "Live E2E Verification Devotee (2 people)",
        "phone_number": unique_phone,
        "gender": "MALE",
        "age": 32,
        "persons_count": 2,
        "purpose_id": None,
        "visitor_date": today_date,
        "visitor_time": now_time,
        "notes": "E2E Verification Registration post fix"
    }

    ts_post = datetime.now(timezone.utc).isoformat()
    req_post = urllib.request.Request(f"{PROD_API_URL}/visitors/", data=json.dumps(payload).encode("utf-8"), headers=headers)
    res_post = safe_urlopen(req_post)
    post_data = json.loads(res_post.read().decode("utf-8"))
    ts_resp = datetime.now(timezone.utc).isoformat()
    print(f"Visitor Registered HTTP {res_post.status}: Session ID {post_data.get('id')}")

    try:
        await asyncio.wait_for(ws_task, timeout=5.0)
    except Exception:
        pass

    # 5. Get Dashboard AFTER
    req_dash_a = urllib.request.Request(f"{PROD_API_URL}/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    dash_after = json.loads(safe_urlopen(req_dash_a).read().decode("utf-8"))
    print(f"Dashboard AFTER registration: {dash_after}")

    # 6. Get Daily Ledger TODAY
    req_ledger = urllib.request.Request(f"{PROD_API_URL}/visitors/ledgers/today", headers={"Authorization": f"Bearer {token}"})
    ledger_today = json.loads(safe_urlopen(req_ledger).read().decode("utf-8"))
    print(f"Daily Ledger TODAY summary: {ledger_today.get('summary')}")

    # Check Parity
    dash_people = dash_after.get("todays_visitors")
    dash_inside = dash_after.get("visitors_inside")
    dash_checkins = dash_after.get("todays_check_ins")

    ledger_people = ledger_today.get("summary", {}).get("total_visitors")
    ledger_inside = ledger_today.get("summary", {}).get("people_inside")
    ledger_sessions_count = len(ledger_today.get("sessions", []))

    print("\nPARITY CHECK RESULTS:")
    print(f"Render API Dashboard People Count: {dash_people} | Ledger Summary People Count: {ledger_people}")
    print(f"Render API Dashboard People Inside: {dash_inside} | Ledger Summary People Inside: {ledger_inside}")
    print(f"Render API Dashboard Check-ins: {dash_checkins} | Ledger Sessions Count: {ledger_sessions_count}")

    parity_pass = (
        dash_people == ledger_people and
        dash_inside == ledger_inside and
        dash_checkins == ledger_sessions_count
    )

    result_summary = {
        "status": "PASS" if parity_pass else "FAIL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit_sha": "3c65ebb0829853400efd0f8ad7bad597e56e43aa",
        "apk_version": "1.9.0+14",
        "visitor_session_id": post_data.get("id"),
        "persons_count": 2,
        "dashboard_after": dash_after,
        "ledger_summary": ledger_today.get("summary"),
        "ws_event_received": ws_received[0] if ws_received else None
    }

    with open("e2e_verification_result.json", "w", encoding="utf-8") as f:
        json.dump(result_summary, f, indent=2)

    print("=" * 80)
    print(f"FINAL E2E VERIFICATION STATUS: {'PASS' if parity_pass else 'FAIL'}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
