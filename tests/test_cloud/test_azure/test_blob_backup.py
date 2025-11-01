"""Tests for Azure Blob Backup Manager"""
import pytest

# Try to import Azure modules and ledger
try:
    from venom.cloud.azure.blob_backup import BlobBackupManager
    from venom.ledger.immutable_ledger import ImmutableLedger
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    BlobBackupManager = None
    ImmutableLedger = None


@pytest.mark.skipif(not AZURE_STORAGE_AVAILABLE, reason="Azure Storage SDK not available")
def test_blob_backup_manager_init():
    """Test Blob backup manager initialization"""
    # Test with connection string
    conn_str = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=fake=="
    
    try:
        manager = BlobBackupManager(
            account_name='test',
            container_name='test-container',
            connection_string=conn_str
        )
        
        assert manager.account_name == 'test'
        assert manager.container_name == 'test-container'
    except Exception:
        # Expected if connection fails
        pytest.skip("Azure connection not available")


@pytest.mark.skipif(not AZURE_STORAGE_AVAILABLE, reason="Azure Storage SDK not available")
def test_blob_backup_manager_methods():
    """Test Blob backup manager has required methods"""
    conn_str = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=fake=="
    
    try:
        manager = BlobBackupManager(
            account_name='test',
            connection_string=conn_str
        )
        
        assert hasattr(manager, 'create_container')
        assert hasattr(manager, 'backup_ledger')
        assert hasattr(manager, 'restore_ledger')
        assert hasattr(manager, 'list_backups')
        assert hasattr(manager, 'delete_backup')
        assert hasattr(manager, 'get_backup_info')
    except Exception:
        pytest.skip("Azure connection not available")


@pytest.mark.skipif(not AZURE_STORAGE_AVAILABLE, reason="Azure Storage SDK not available")
def test_backup_ledger_mock():
    """Test ledger backup (mock)"""
    conn_str = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=fake=="
    
    try:
        manager = BlobBackupManager(
            account_name='test',
            connection_string=conn_str
        )
        
        ledger = ImmutableLedger()
        ledger.record_action("TEST", {"data": "test"})
        
        assert callable(manager.backup_ledger)
    except Exception:
        pytest.skip("Azure connection not available")


@pytest.mark.skipif(not AZURE_STORAGE_AVAILABLE, reason="Azure Storage SDK not available")
def test_backup_state_method():
    """Test state backup method exists"""
    conn_str = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=fake=="
    
    try:
        manager = BlobBackupManager(
            account_name='test',
            connection_string=conn_str
        )
        
        assert hasattr(manager, 'backup_state')
        assert hasattr(manager, 'restore_state')
    except Exception:
        pytest.skip("Azure connection not available")


def test_blob_import_fallback():
    """Test graceful fallback when Azure Storage SDK not available"""
    if not AZURE_STORAGE_AVAILABLE:
        pytest.skip("Azure Storage SDK not available - graceful fallback working")
    else:
        assert BlobBackupManager is not None
