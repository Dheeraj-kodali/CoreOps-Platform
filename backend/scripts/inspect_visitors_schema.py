import asyncio
import json
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def inspect_schema():
    async with AsyncSessionLocal() as session:
        # Get column names of visitors table
        sql_cols = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'visitors'
            ORDER BY ordinal_position;
        """)
        res = await session.execute(sql_cols)
        cols = [dict(r) for r in res.mappings().all()]
        print("COLUMNS IN 'visitors' TABLE:")
        for c in cols:
            print(f"  {c['column_name']}: {c['data_type']}")

        # Query all records without status column
        sql_sample = text("""
            SELECT * FROM visitors LIMIT 5;
        """)
        res_sample = await session.execute(sql_sample)
        sample_rows = [dict(r) for r in res_sample.mappings().all()]
        print("\nSAMPLE ROWS IN 'visitors' TABLE:")
        print(json.dumps(sample_rows, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(inspect_schema())
