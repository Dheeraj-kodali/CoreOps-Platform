# Operations Manual — Temple Visitor Management System Enterprise Edition v2.0

## 1. Overview
The Temple Visitor Management System Enterprise Edition v2.0 is an offline-first multi-tenant visitor registration, checkout, analytics, delta-synchronization, immutable audit, and Meta WhatsApp broadcast platform.

## 2. System Architecture & Components
- **Backend Core**: FastAPI (Python 3.14+), Uvicorn ASGI, SQLAlchemy 2.0 Async, aiosqlite.
- **Primary Database**: SQLite3 with Write-Ahead Logging (WAL) mode enabled (`temple.db`).
- **Sync Engine**: Transactional Outbox Pattern & Delta Sync (`SyncQueue`).
- **Broadcast System**: Asynchronous Queue Worker & Meta WhatsApp Cloud API v23.0.
- **Mobile Kiosk App**: Flutter 3.x Tablet & Mobile Application (`mobile/`).
- **Owner & Operational Dashboard**: React / Next.js 14 Web Application (`admin/`).

## 3. Worker Vitality & Heartbeat Monitoring
Background tasks (Scheduler, Queue Worker, Heartbeat Ticker) run continuously inside the FastAPI process loop.
- **Heartbeat Endpoint**: `GET /api/v2/health/system`
- **Automatic Recovery**: If the service restarts after an unexpected crash, `WorkerResilienceManager` detects stuck campaigns in `SENDING` status and automatically resets them to `QUEUED` for safe re-execution.

## 4. Disaster Recovery & Emergency Contacts
- Emergency Database Restore: Execute `python -c "import asyncio; from app.core.backup_manager import BackupManager; asyncio.run(BackupManager.restore_database_from_backup('./backups/temple_backup_latest.db'))"`
