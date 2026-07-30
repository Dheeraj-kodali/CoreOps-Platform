import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"), override=True)

import app.models
from app.core.config import settings
from app.core.database import Base
import sqlalchemy as sa

engine = sa.create_engine(settings.SYNC_DATABASE_URL)
print("Creating all tables in Neon PostgreSQL...")
Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    conn.execute(sa.text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(255) PRIMARY KEY);"))
    conn.execute(sa.text("TRUNCATE alembic_version;"))
    conn.execute(sa.text("INSERT INTO alembic_version (version_num) VALUES ('006_v8_neon_postgresql');"))
    conn.commit()

print("✓ All tables created successfully in Neon PostgreSQL and alembic_version set to '006_v8_neon_postgresql'!")
