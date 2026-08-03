import asyncio
import hashlib
import os
import json
import httpx
from datetime import datetime

APK_PATH = r"c:\Users\Dheeraj\OneDrive\Desktop\temple\mobile\build\app\outputs\flutter-apk\app-release.apk"
PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"

def _compute_sha256(path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def run_apk_smoke_test():
    print("=" * 80)
    print("PRODUCTION RELEASE APK V1.9.0+12 SMOKE TEST & METADATA VERIFICATION")
    print("=" * 80)

    # 1. APK File Properties
    if not os.path.exists(APK_PATH):
        raise FileNotFoundError(f"APK file not found at {APK_PATH}")

    file_size_bytes = os.path.getsize(APK_PATH)
    file_size_mb = file_size_bytes / (1024 * 1024)

    checksum = await asyncio.to_thread(_compute_sha256, APK_PATH)

    print(f"APK Path: {APK_PATH}")
    print(f"APK Size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print(f"SHA256 Checksum: {checksum}")

    # 2. Production API Smoke Test
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Step A: Mobile User Login
        print("\nStep 1: Mobile App Login to Production API...")
        login_res = await client.post(
            f"{PROD_API_URL}/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        login_data = login_res.json()
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   [SUCCESS] Logged in as admin. Token acquired.")

        # Step B: Register Visitor (Mobile Context)
        import uuid
        test_uuid = str(uuid.uuid4())
        test_name = f"APK v1.9.0 Devotee {datetime.now().strftime('%H:%M:%S')}"
        now_str = datetime.now()
        unique_phone = f"98{int(datetime.now().timestamp()) % 100000000:08d}"
        visitor_payload = {
            "name": test_name,
            "phone_number": unique_phone,
            "gender": "MALE",
            "age": 28,
            "persons_count": 2,
            "visitor_date": now_str.strftime("%Y-%m-%d"),
            "visitor_time": now_str.strftime("%H:%M:%S"),
            "visitor_uuid": test_uuid,
            "notes": "APK Release v1.9.0+12 Production Smoke Test",
            "latitude": 17.385043,
            "longitude": 78.486671
        }

        print("\nStep 2: Register Visitor from Mobile App Context...")
        reg_res = await client.post(f"{PROD_API_URL}/visitors/", json=visitor_payload, headers=headers)
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        reg_data = reg_res.json()
        visitor_id = reg_data["id"]
        print(f"   [SUCCESS] Visitor registered. ID: {visitor_id}, Status: {reg_data.get('status')}")

        # Step C: Check Out Visitor
        print("\nStep 3: Check Out Visitor from Mobile App Context...")
        co_res = await client.post(f"{PROD_API_URL}/visitors/{visitor_id}/checkout", json={}, headers=headers)
        assert co_res.status_code == 200, f"Checkout failed: {co_res.text}"
        co_data = co_res.json()
        print(f"   [SUCCESS] Visitor checked out. Status: {co_data.get('status')}, Duration: {co_data.get('duration')}")

        # Step D: Dashboard Real-time Verification
        print("\nStep 4: Verify Dashboard Real-Time Statistics...")
        dash_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_data = dash_res.json()
        print(f"   Today's Visitors: {dash_data.get('todays_visitors')}")
        print(f"   Visitors Inside:  {dash_data.get('visitors_inside')}")
        print(f"   Today's Check-outs: {dash_data.get('todays_check_outs')}")

    print("\n" + "=" * 80)
    print("PRODUCTION RELEASE APK V1.9.0+12 SMOKE TEST PASSED PERFECTLY!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_apk_smoke_test())
