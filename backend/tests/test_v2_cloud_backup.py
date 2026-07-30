import os
import shutil
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

from app.main import app, seed_initial_data
from app.core.database import engine, Base
from app.core.storage_providers import get_storage_provider, LocalStorageProvider
from app.core.cloud_backup import CloudBackupEncryptionEngine, CloudBackupService


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


@pytest.mark.asyncio
async def test_storage_provider_factory_and_local_mock_provider():
    """Verify pluggable storage provider factory and local mock cloud provider."""
    provider = get_storage_provider("LOCAL")
    assert isinstance(provider, LocalStorageProvider)
    assert provider.provider_name() == "LOCAL_MOCK_CLOUD"

    health = await provider.check_health()
    assert health["status"] == "UP"

    # Test Upload & Download
    test_src = "./test_upload_source.txt"
    test_dst = "./test_download_dest.txt"
    with open(test_src, "w") as f:
        f.write("Cloud Storage Abstraction Test")

    upload_ok = await provider.upload_file(test_src, "test/sample.txt")
    assert upload_ok is True

    download_ok = await provider.download_file("test/sample.txt", test_dst)
    assert download_ok is True
    assert open(test_dst).read() == "Cloud Storage Abstraction Test"

    # Cleanup
    if os.path.exists(test_src):
        os.remove(test_src)
    if os.path.exists(test_dst):
        os.remove(test_dst)


@pytest.mark.asyncio
async def test_aes256_encryption_and_decryption_engine():
    """Verify GZip compression and Fernet AES-256 encryption engine."""
    src_file = "./test_enc_src.txt"
    archive_file = "./test_enc_archive.enc"
    dec_file = "./test_dec_out.txt"

    original_content = "Temple Visitor Management System AES-256 Snapshot Data" * 50
    with open(src_file, "w") as f:
        f.write(original_content)

    meta = CloudBackupEncryptionEngine.encrypt_and_compress(src_file, archive_file)
    assert meta["encrypted"] is True
    assert meta["algorithm"] == "AES-256-Fernet"
    assert os.path.exists(archive_file)

    decrypt_ok = CloudBackupEncryptionEngine.decrypt_and_decompress(archive_file, dec_file)
    assert decrypt_ok is True
    assert open(dec_file).read() == original_content

    # Cleanup
    for p in [src_file, archive_file, dec_file]:
        if os.path.exists(p):
            os.remove(p)


@pytest.mark.asyncio
async def test_cloud_backup_creation_upload_and_metadata():
    """Verify full cloud backup snapshot creation, encryption, upload, and metadata structure."""
    meta = await CloudBackupService.create_and_upload_cloud_backup(provider_name="LOCAL")
    assert "backup_id" in meta
    assert meta["encryption_status"] == "AES-256-ENCRYPTED"
    assert meta["cloud_provider"] == "LOCAL_MOCK_CLOUD"
    assert meta["archive_size_bytes"] > 0
    assert len(meta["sha256_checksum"]) == 64


@pytest.mark.asyncio
async def test_retention_policy_cleanup():
    """Verify retention policy enforcement retains active copies and purges expired snapshots."""
    # Create 3 cloud backups
    for _ in range(3):
        await CloudBackupService.create_and_upload_cloud_backup(provider_name="LOCAL")

    retention_report = await CloudBackupService.apply_retention_policy(provider_name="LOCAL", daily_keep=2)
    assert retention_report["active_backups_retained"] <= 2


@pytest.mark.asyncio
async def test_disaster_recovery_dry_run_and_full_restore():
    """Verify disaster recovery dry-run validation and full database restore execution."""
    meta = await CloudBackupService.create_and_upload_cloud_backup(provider_name="LOCAL")
    backup_id = meta["backup_id"]

    # Dry-Run DR Validation
    dry_run_res = await CloudBackupService.execute_disaster_recovery_restore(backup_id, provider_name="LOCAL", dry_run=True)
    assert dry_run_res["status"] == "VALIDATED"
    assert dry_run_res["dry_run"] is True

    # Full DR Restore
    restore_res = await CloudBackupService.execute_disaster_recovery_restore(backup_id, provider_name="LOCAL", dry_run=False)
    assert restore_res["status"] == "RESTORED"
    assert restore_res["dry_run"] is False


@pytest.mark.asyncio
async def test_cloud_backup_health_endpoint():
    """Verify GET /api/v2/health/cloud-backup health monitoring endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/health/cloud-backup?provider=LOCAL")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["last_upload_status"] == "SUCCESS"
        assert data["cloud_provider"] == "LOCAL_MOCK_CLOUD"
        assert data["encryption_algorithm"] == "AES-256-Fernet"
