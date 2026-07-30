# Production Deployment Guide - v2.0
## Temple Visitor Management System Enterprise Edition

### 1. Pre-Deployment Requirements
- **Server OS**: Ubuntu 22.04 LTS / Debian 12 / Docker Container
- **Python**: Python 3.14+
- **Cloud Database**: Neon PostgreSQL 18 instance with SSL (`sslmode=require`)
- **Process Manager**: Systemd / Gunicorn / Uvicorn

---

### 2. Environment Configuration
Create `/etc/temple/backend.env` or `backend/.env`:
```ini
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_password@ep-host.aws.neon.tech/neondb?sslmode=require
SYNC_DATABASE_URL=postgresql://neondb_owner:npg_password@ep-host.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=prod_jwt_super_secret_key_88776655443322
BACKUP_ENCRYPTION_KEY=sk_temple_v2_cloud_backup_master_aes256_key_9988
CORS_ORIGINS=["https://dashboard.temple-vms.example.com"]
```

---

### 3. Database Migration & Table Initialization
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Apply Alembic Migrations
alembic upgrade head
```

---

### 4. Running Production Systemd Service
Create `/etc/systemd/system/temple-backend.service`:
```ini
[Unit]
Description=Temple VMS FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/temple/backend
ExecStart=/var/www/temple/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable temple-backend
sudo systemctl start temple-backend
```

---

### 5. Flutter Mobile App Release Build
```bash
cd mobile
flutter clean
flutter pub get
flutter build apk --release
```
The generated APK file will be located at `mobile/build/app/outputs/flutter-apk/app-release.apk`.
