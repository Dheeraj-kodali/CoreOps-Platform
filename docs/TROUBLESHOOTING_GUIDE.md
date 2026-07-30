# Troubleshooting Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Database Lock / Busy Errors (`sqlite3.OperationalError: database is locked`)
- **Root Cause**: WAL mode disabled or long sync transaction holding write lock.
- **Remediation**: Verify WAL mode: `PRAGMA journal_mode=WAL;` in SQLite.

## 2. Broadcast Queue Stuck in SENDING
- **Root Cause**: Unexpected server crash during batch dispatch.
- **Remediation**: Trigger worker recovery endpoint or call `WorkerResilienceManager.recover_stuck_broadcast_jobs()`.

## 3. Meta WhatsApp Dispatch 400/401 Errors
- **Root Cause**: Expired Meta Access Token or invalid Phone Number ID.
- **Remediation**: Update access token under Communication Settings in Admin Dashboard.
