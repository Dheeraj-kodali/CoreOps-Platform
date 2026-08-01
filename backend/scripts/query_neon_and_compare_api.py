import asyncio
import json
import httpx
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"

async def run_comparison():
    print("=" * 80)
    print("DIRECT NEON POSTGRESQL QUERY vs LIVE PRODUCTION API COMPARISON")
    print("=" * 80)

    # 1. Execute SQL Queries directly on Neon PostgreSQL
    async with AsyncSessionLocal() as session:
        # Query 1: Overall production statistics
        sql1 = text("""
            SELECT
                COUNT(*) AS visitor_records,
                COALESCE(SUM(persons_count),0) AS total_people,
                COALESCE(SUM(CASE WHEN status='INSIDE' THEN persons_count ELSE 0 END),0) AS people_inside,
                COALESCE(SUM(CASE WHEN status='CHECKED_OUT' THEN persons_count ELSE 0 END),0) AS people_checked_out
            FROM visitors
            WHERE is_deleted = FALSE;
        """)
        res1 = await session.execute(sql1)
        row1 = dict(res1.mappings().one())

        # Query 2: Today's statistics
        sql2 = text("""
            SELECT
                COUNT(*) AS visitor_records_today,
                COALESCE(SUM(persons_count),0) AS total_people_today,
                COALESCE(SUM(CASE WHEN status='INSIDE' THEN persons_count ELSE 0 END),0) AS people_inside_today,
                COALESCE(SUM(CASE WHEN status='CHECKED_OUT' THEN persons_count ELSE 0 END),0) AS people_checked_out_today
            FROM visitors
            WHERE visitor_date = CURRENT_DATE
            AND is_deleted = FALSE;
        """)
        res2 = await session.execute(sql2)
        row2 = dict(res2.mappings().one())

        # Query 3: List all today's visitors
        sql3 = text("""
            SELECT
                id,
                visitor_uuid,
                name,
                persons_count,
                status,
                visitor_date,
                visitor_time,
                created_at
            FROM visitors
            WHERE visitor_date = CURRENT_DATE
            ORDER BY created_at DESC;
        """)
        res3 = await session.execute(sql3)
        rows3 = [dict(r) for r in res3.mappings().all()]

    print("\n--- 1. OVERALL NEON POSTGRESQL STATISTICS ---")
    print(json.dumps(row1, indent=2, default=str))

    print("\n--- 2. TODAY'S NEON POSTGRESQL STATISTICS ---")
    print(json.dumps(row2, indent=2, default=str))

    print("\n--- 3. ALL TODAY'S VISITORS IN NEON POSTGRESQL ---")
    print(json.dumps(rows3, indent=2, default=str))

    # 2. Fetch Live Production API Endpoints
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Authenticate
        login_res = await client.post(
            f"{PROD_API_URL}/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # GET /api/v1/analytics/dashboard
        dash_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_data = dash_res.json()

        # GET /api/v1/visitors
        visitors_res = await client.get(f"{PROD_API_URL}/visitors/", headers=headers)
        visitors_data = visitors_res.json()

    print("\n--- 4. GET /api/v1/analytics/dashboard RESPONSE ---")
    print(json.dumps(dash_data, indent=2, default=str))

    print("\n--- 5. GET /api/v1/visitors RESPONSE (Sample / Summary) ---")
    if isinstance(visitors_data, list):
        print(f"Total Visitor Items Returned: {len(visitors_data)}")
        print("First 3 items:")
        print(json.dumps(visitors_data[:3], indent=2, default=str))
    elif isinstance(visitors_data, dict):
        print(f"Total Visitors Count: {visitors_data.get('total')}")
        print("Sample items:")
        print(json.dumps(visitors_data.get('items', [])[:3], indent=2, default=str))

    out_data = {
        "sql_overall": row1,
        "sql_todays": row2,
        "sql_todays_list": rows3,
        "api_dashboard": dash_data,
        "api_visitors": visitors_data
    }

    with open("neon_vs_api_comparison.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print("NEON DB vs API DATA EXTRACTION COMPLETE. Saved to neon_vs_api_comparison.json")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_comparison())
