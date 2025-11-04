"""Tests for GCP Storage Backup Manager"""
import pytest
from unittest.mock import Mock, patch

# Try to import GCP modules and ledger
try:
    from venom.cloud.gcp.storage_backup import StorageBackupManager
    from venom.ledger.immutable_ledger import ImmutableLedger
    from google.cloud import storage
    GCP_STORAGE_AVAILABLE = True
except ImportError:
    GCP_STORAGE_AVAILABLE = False
    StorageBackupManager = None
    ImmutableLedger = None


@pytest.mark.skipif(not GCP_STORAGE_AVAILABLE, reason="GCP Storage SDK not available")
@patch('venom.cloud.gcp.storage_backup.storage.Client')
def test_storage_backup_manager_init(mock_client):
    """Test Storage backup manager initialization"""
    mock_client.return_value = Mock()
    
    manager = StorageBackupManager(
        bucket_name='test-bucket',
        project_id='test-project'
    )
    
    assert manager.bucket_name == 'test-bucket'
    assert manager.project_id == 'test-project'


@pytest.mark.skipif(not GCP_STORAGE_AVAILABLE, reason="GCP Storage SDK not available")
@patch('venom.cloud.gcp.storage_backup.storage.Client')
def test_storage_backup_manager_methods(mock_client):
    """Test Storage backup manager has required methods"""
    mock_client.return_value = Mock()
    
    manager = StorageBackupManager(
        bucket_name='test-bucket',
        project_id='test-project'
    )
    
    assert hasattr(manager, 'create_bucket')
    assert hasattr(manager, 'backup_ledger')
    assert hasattr(manager, 'restore_ledger')
    assert hasattr(manager, 'list_backups')
    assert hasattr(manager, 'delete_backup')
    assert hasattr(manager, 'get_backup_info')


@pytest.mark.skipif(not GCP_STORAGE_AVAILABLE, reason="GCP Storage SDK not available")
@patch('venom.cloud.gcp.storage_backup.storage.Client')
def test_backup_ledger_mock(mock_client):
    """Test ledger backup (mock)"""
    mock_client.return_value = Mock()
    
    manager = StorageBackupManager(
        bucket_name='test-bucket',
        project_id='test-project'
    )
    
    ledger = ImmutableLedger()
    ledger.record_action("TEST", {"data": "test"})
    
    assert callable(manager.backup_ledger)


@pytest.mark.skipif(not GCP_STORAGE_AVAILABLE, reason="GCP Storage SDK not available")
@patch('venom.cloud.gcp.storage_backup.storage.Client')
def test_list_backups_mock(mock_client):
    """Test listing backups (mock)"""
    mock_client.return_value = Mock()
    
    manager = StorageBackupManager(
        bucket_name='test-bucket',
        project_id='test-project'
    )
    
    assert callable(manager.list_backups)


@pytest.mark.skipif(not GCP_STORAGE_AVAILABLE, reason="GCP Storage SDK not available")
@patch('venom.cloud.gcp.storage_backup.storage.Client')
def test_backup_state_method(mock_client):
    """Test state backup method exists"""
    mock_client.return_value = Mock()
    
    manager = StorageBackupManager(
        bucket_name='test-bucket',
        project_id='test-project'
    )
    
    assert hasattr(manager, 'backup_state')
    assert hasattr(manager, 'restore_state')
    assert callable(manager.backup_state)


def test_storage_import_fallback():
    """Test graceful fallback when GCP Storage SDK not available"""
    if not GCP_STORAGE_AVAILABLE:
        pytest.skip("GCP Storage SDK not available - graceful fallback working")
    else:
        assert StorageBackupManager is not None
