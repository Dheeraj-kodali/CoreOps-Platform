# Provider Configuration Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Environment Variable Configuration

### AWS S3 / Cloudflare R2 / MinIO
```env
CLOUD_STORAGE_PROVIDER=AWS_S3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET_NAME=temple-visitor-backups
AWS_REGION=ap-south-1
```

### Azure Blob Storage
```env
CLOUD_STORAGE_PROVIDER=AZURE_BLOB
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=templebackup..."
AZURE_CONTAINER_NAME=backups
```

### Google Cloud Storage
```env
CLOUD_STORAGE_PROVIDER=GCS
GCS_BUCKET_NAME=temple-visitor-backups
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp_service_account.json
```
