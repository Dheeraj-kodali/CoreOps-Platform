# Monitoring & Observability Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Production Health Endpoints
- `GET /api/v2/health` — System Readiness & Status
- `GET /api/v2/health/database` — SQLite Latency, WAL Mode & DB Size
- `GET /api/v2/health/sync` — Sync Queue Backlog & Failures
- `GET /api/v2/health/broadcast` — Active Broadcast Campaigns & Recipient Queue
- `GET /api/v2/health/system` — Memory RSS (MB), CPU Load %, Disk Free (GB)

## 2. Structured JSON Logs
Application logs are output in single-line JSON format on `sys.stdout`.
Filter critical errors: `grep '"level":"ERROR"' /var/log/temple.log`
