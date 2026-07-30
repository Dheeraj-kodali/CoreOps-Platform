# Neon PostgreSQL Setup & Integration Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Overview
The Temple Visitor Management System Enterprise Edition v2.0 integrates **Neon PostgreSQL** as its primary cloud database layer, while maintaining the offline-first SQLite database on edge nodes (Flutter mobile app).

---

## 2. Step-by-Step Provisioning Protocol

### Step 1: Create a Neon Project
1. Log in to [Neon Console](https://console.neon.tech).
2. Click **Create Project**.
3. Name your project: `temple-visitor-management`.
4. Select region (e.g. `ap-south-1` / `aws-ap-south-1`).
5. Select PostgreSQL version `15+`.

### Step 2: Retrieve the Connection String
1. Go to your project **Dashboard** in Neon.
2. Under **Connection Details**, select **PostgreSQL** and **pooled connection**.
3. Copy the asyncpg and psycopg2 connection strings:
   - Async Connection (`postgresql+asyncpg`):
     ```
     postgresql+asyncpg://<user>:<password>@<neon_host>/<dbname>?sslmode=require
     ```
   - Sync Migration Connection (`postgresql`):
     ```
     postgresql://<user>:<password>@<neon_host>/<dbname>?sslmode=require
     ```

### Step 3: Paste Credentials into `backend/.env`
Paste your credentials into `backend/.env`:
```env
DATABASE_URL="postgresql+asyncpg://<user>:<password>@<neon_host>/<dbname>?sslmode=require"
SYNC_DATABASE_URL="postgresql://<user>:<password>@<neon_host>/<dbname>?sslmode=require"
```

### Step 4: Run Alembic Database Migrations
```bash
cd backend
python -m alembic upgrade head
```

---

## 3. Security & Best Practices
- **Never commit `.env`**: Credentials must remain exclusively inside `backend/.env` (which is git-ignored).
- **SSL Enforcement**: `sslmode=require` is enforced for all Neon server connections.
- **Connection Pooling**: SQLAlchemy connection pool (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`) handles Neon serverless compute suspend and auto-reconnects seamlessly.
