# Environment Variables Guide — Temple Visitor Management System Enterprise Edition v2.0

## Specification Matrix

| Variable Name | Required | Default Value | Purpose / Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Yes | `production` | Deployment environment mode (`production`, `staging`, `development`) |
| `PROJECT_NAME` | No | `"Sri Kalki Seva..."` | Application title |
| `SECRET_KEY` | Yes | (Required) | Application secret key for token signing and session security |
| `JWT_SECRET` | Yes | (Required) | Secret key for JWT Bearer token generation |
| `DATABASE_URL` | **CRITICAL** | (No Default) | Primary database connection string (`postgresql+asyncpg://...` or `sqlite+aiosqlite://...`) |
| `SYNC_DATABASE_URL` | Yes | (Optional) | Alembic migration connection string (`postgresql://...` or `sqlite://...`) |
| `REDIS_URL` | Optional | `redis://localhost:6379/0` | Redis caching & pub/sub broker |
| `CELERY_BROKER_URL` | Optional | `redis://localhost:6379/0` | Celery task queue broker |
| `SMS_API_KEY` | Optional | `""` | SMS gateway API credentials |
| `WHATSAPP_ACCESS_TOKEN` | Optional | `""` | Meta WhatsApp Cloud API access token |
| `CLOUD_STORAGE_PROVIDER` | Optional | `LOCAL` | Multi-cloud provider driver (`AWS_S3`, `AZURE_BLOB`, `GCS`, `CLOUDFLARE_R2`, etc.) |
| `BACKUP_ENCRYPTION_KEY` | Optional | Derived | Secret phrase for 256-bit Fernet AES-256 cloud snapshot encryption |

---

## Startup Failure Guarantee
If `DATABASE_URL` is omitted or empty, the application aborts initialization immediately with error:
```
ValueError: CRITICAL STARTUP FAILURE: DATABASE_URL environment variable is missing or empty. Please configure DATABASE_URL in backend/.env file.
```
