# Cloud Backup Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. System Overview & Isolation
The Cloud Backup Service provides multi-cloud snapshot backups for emergency disaster recovery.
**Critical Rule**: Cloud Backup and Cloud Sync (delta synchronization) remain strictly separate systems. Cloud Sync manages real-time visitor event syncing, while Cloud Backup manages encrypted whole-database disaster recovery snapshots.

## 2. Pluggable Storage Providers
Supported providers via `BaseStorageProvider`:
- **AWS S3** (`AWS_S3`)
- **Azure Blob Storage** (`AZURE_BLOB`)
- **Google Cloud Storage** (`GCS`)
- **Cloudflare R2** (`CLOUDFLARE_R2`)
- **Backblaze B2** (`BACKBLAZE_B2`)
- **MinIO S3-Compatible** (`MINIO_S3`)
- **Local / Mock Provider** (`LOCAL_MOCK_CLOUD`)

## 3. Encryption & Compression Standard
- Archive Compression: `gzip`
- Encryption Standard: **AES-256-Fernet** with 32-byte SHA-256 key derivative (`BACKUP_ENCRYPTION_KEY`).
- Secret Key Safety: Credentials, tokens, and encryption keys are configured exclusively via environment variables and masked in all log outputs.
