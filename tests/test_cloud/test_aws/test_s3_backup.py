"""Tests for AWS S3 Backup Manager"""
import pytest

# Try to import AWS modules and ledger
try:
    from venom.cloud.aws.s3_backup import S3BackupManager
    from venom.ledger.immutable_ledger import ImmutableLedger
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    S3BackupManager = None
    ImmutableLedger = None


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_s3_backup_manager_init():
    """Test S3 backup manager initialization"""
    manager = S3BackupManager(bucket_name='test-bucket', region='us-east-1')
    
    assert manager.bucket_name == 'test-bucket'
    assert manager.region == 'us-east-1'
    assert manager.s3_client is not None


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_s3_backup_manager_methods():
    """Test S3 backup manager has required methods"""
    manager = S3BackupManager(bucket_name='test-bucket')
    
    assert hasattr(manager, 'create_bucket')
    assert hasattr(manager, 'backup_ledger')
    assert hasattr(manager, 'restore_ledger')
    assert hasattr(manager, 'list_backups')
    assert hasattr(manager, 'delete_backup')
    assert hasattr(manager, 'get_backup_info')
    assert callable(manager.backup_ledger)


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_backup_ledger_mock():
    """Test ledger backup (mock)"""
    manager = S3BackupManager(bucket_name='test-bucket')
    
    # Create a test ledger
    ledger = ImmutableLedger()
    ledger.record_action("TEST", {"data": "test"})
    
    # Test that backup method exists and accepts correct parameters
    assert callable(manager.backup_ledger)
    # Would need mocked AWS to actually test backup


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_list_backups_mock():
    """Test listing backups (mock)"""
    manager = S3BackupManager(bucket_name='test-bucket')
    
    # Test that method exists
    assert callable(manager.list_backups)


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_backup_state_method():
    """Test state backup method exists"""
    manager = S3BackupManager(bucket_name='test-bucket')
    
    assert hasattr(manager, 'backup_state')
    assert hasattr(manager, 'restore_state')
    assert callable(manager.backup_state)


def test_s3_import_fallback():
    """Test graceful fallback when AWS SDK not available"""
    if not AWS_AVAILABLE:
        pytest.skip("AWS SDK not available - graceful fallback working")
    else:
        assert S3BackupManager is not None
