import asyncio
import json
import httpx
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

PROD_API_URL = "https://coreops-platform.onrender.com/api/v1"

async def run_raw_verification():
    print("=" * 80)
    print("NEON POSTGRESQL DIRECT SQL & LIVE API COMPARISON")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        # 1. Overall Production Statistics SQL
        sql1 = text("""
            SELECT
                COUNT(*) AS visitor_records,
                COALESCE(SUM(persons_count),0) AS total_people,
                COALESCE(SUM(CASE WHEN (notes LIKE '%CHECKED_OUT%' OR notes LIKE '%Visitor Left%' OR notes LIKE '%Exit Time%') THEN 0 ELSE persons_count END),0) AS people_inside,
                COALESCE(SUM(CASE WHEN (notes LIKE '%CHECKED_OUT%' OR notes LIKE '%Visitor Left%' OR notes LIKE '%Exit Time%') THEN persons_count ELSE 0 END),0) AS people_checked_out
            FROM visitors
            WHERE is_deleted = FALSE;
        """)
        res1 = await session.execute(sql1)
        row1 = dict(res1.mappings().one())

        # 2. Today's Statistics SQL
        sql2 = text("""
            SELECT
                COUNT(*) AS visitor_records_today,
                COALESCE(SUM(persons_count),0) AS total_people_today,
                COALESCE(SUM(CASE WHEN (notes LIKE '%CHECKED_OUT%' OR notes LIKE '%Visitor Left%' OR notes LIKE '%Exit Time%') THEN 0 ELSE persons_count END),0) AS people_inside_today,
                COALESCE(SUM(CASE WHEN (notes LIKE '%CHECKED_OUT%' OR notes LIKE '%Visitor Left%' OR notes LIKE '%Exit Time%') THEN persons_count ELSE 0 END),0) AS people_checked_out_today
            FROM visitors
            WHERE visitor_date = CURRENT_DATE
            AND is_deleted = FALSE;
        """)
        res2 = await session.execute(sql2)
        row2 = dict(res2.mappings().one())

        # 3. List All Today's Visitors SQL
        sql3 = text("""
            SELECT
                id,
                visitor_uuid,
                name,
                persons_count,
                CASE WHEN (notes LIKE '%CHECKED_OUT%' OR notes LIKE '%Visitor Left%' OR notes LIKE '%Exit Time%') THEN 'CHECKED_OUT' ELSE 'INSIDE' END AS status,
                visitor_date,
                visitor_time,
                created_at
            FROM visitors
            WHERE visitor_date = CURRENT_DATE
            ORDER BY created_at DESC;
        """)
        res3 = await session.execute(sql3)
        rows3 = [dict(r) for r in res3.mappings().all()]

    # Live API Requests
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        login_res = await client.post(
            f"{PROD_API_URL}/auth/login",
            json={"username": "admin", "password": "Admin@12345"}
        )
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        dash_res = await client.get(f"{PROD_API_URL}/analytics/dashboard", headers=headers)
        dash_data = dash_res.json()

        visitors_res = await client.get(f"{PROD_API_URL}/visitors/", headers=headers)
        visitors_data = visitors_res.json()

    print("\n1. OVERALL PRODUCTION STATISTICS (SQL):")
    print(json.dumps(row1, indent=2, default=str))

    print("\n2. TODAY'S STATISTICS (SQL):")
    print(json.dumps(row2, indent=2, default=str))

    print("\n3. TODAY'S VISITORS LIST (SQL):")
    print(json.dumps(rows3, indent=2, default=str))

    print("\n4. GET /api/v1/analytics/dashboard RESPONSE:")
    print(json.dumps(dash_data, indent=2, default=str))

    print("\n5. GET /api/v1/visitors RESPONSE:")
    print(json.dumps(visitors_data, indent=2, default=str))

    out_payload = {
        "sql_overall": row1,
        "sql_todays": row2,
        "sql_todays_visitors": rows3,
        "api_dashboard": dash_data,
        "api_visitors": visitors_data
    }

    with open("neon_sql_raw_results.json", "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print("NEON SQL RAW EXECUTION COMPLETE.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_raw_verification())
