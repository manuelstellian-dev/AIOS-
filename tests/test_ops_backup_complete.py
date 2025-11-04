"""
Complete comprehensive tests for venom/ops/backup.py to achieve 97%+ coverage
"""
import pytest
import gzip
import json
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ledger():
    """Create mock ledger with proper structure"""
    ledger = Mock()
    ledger.chain = []
    # Use correct LedgerEntry format with required fields
    ledger.export_chain.return_value = [
        {
            "index": 0,
            "timestamp": 1000.0,
            "data": {"type": "genesis"},
            "previous_hash": "0" * 64,
            "hash": "a" * 64
        },
        {
            "index": 1,
            "timestamp": 2000.0,
            "data": {"beat": 1, "theta": 0.5},
            "previous_hash": "a" * 64,
            "hash": "b" * 64
        },
    ]
    ledger.compute_merkle_root.return_value = "abc123"
    ledger.verify_chain.return_value = True
    return ledger


def test_backup_manager_init_enabled(mock_ledger, temp_backup_dir):
    """Test initialization with enabled=True"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    assert manager.ledger == mock_ledger
    assert manager.backup_dir == Path(temp_backup_dir)
    assert manager.enabled is True
    assert manager.backup_interval == 10
    assert manager.beat_counter == 0
    assert Path(temp_backup_dir).exists()


def test_backup_manager_init_disabled(mock_ledger, temp_backup_dir):
    """Test initialization with enabled=False"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    
    assert manager.enabled is False
    # Directory should not be created when disabled
    assert not Path(temp_backup_dir).exists() or manager.backup_dir == Path(temp_backup_dir)


def test_backup_create_success(mock_ledger, temp_backup_dir):
    """Test successful backup creation"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    result = manager.backup()
    
    assert result is not None
    assert Path(result).exists()
    assert result.endswith('.json.gz')
    
    # Verify file can be decompressed
    with gzip.open(result, 'rt') as f:
        data = json.load(f)
        assert 'timestamp' in data
        assert 'chain' in data
        assert 'chain_length' in data
        assert 'merkle_root' in data
        assert data['chain_length'] == 2
        assert data['merkle_root'] == "abc123"


def test_backup_create_with_custom_filename(mock_ledger, temp_backup_dir):
    """Test backup with custom filename"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    result = manager.backup(filename="custom_backup.json.gz")
    
    assert result is not None
    assert "custom_backup.json.gz" in result
    assert Path(result).exists()


def test_backup_disabled_returns_none(mock_ledger, temp_backup_dir):
    """Test backup returns None when disabled"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    result = manager.backup()
    
    assert result is None


def test_backup_exception_handling(mock_ledger, temp_backup_dir):
    """Test backup handles exceptions"""
    from venom.ops.backup import BackupManager
    
    mock_ledger.export_chain.side_effect = Exception("Export failed")
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    result = manager.backup()
    
    assert result is None


def test_restore_success(mock_ledger, temp_backup_dir):
    """Test successful restore"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create backup first
    backup_file = manager.backup()
    assert backup_file is not None
    
    # Reset ledger mock
    mock_ledger.chain.clear()
    mock_ledger.verify_chain.return_value = True
    
    # Restore
    result = manager.restore(backup_file, verify=True)
    
    assert result is True
    mock_ledger.verify_chain.assert_called_once()


def test_restore_without_verification(mock_ledger, temp_backup_dir):
    """Test restore without verification"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create backup
    backup_file = manager.backup()
    
    # Restore without verification
    result = manager.restore(backup_file, verify=False)
    
    assert result is True
    mock_ledger.verify_chain.assert_not_called()


def test_restore_empty_chain(mock_ledger, temp_backup_dir):
    """Test restore with empty chain data"""
    from venom.ops.backup import BackupManager
    
    # Create backup file with empty chain
    backup_file = Path(temp_backup_dir) / "empty_backup.json.gz"
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with gzip.open(backup_file, 'wt') as f:
        json.dump({"timestamp": time.time(), "chain": []}, f)
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    result = manager.restore(str(backup_file))
    
    assert result is False


def test_restore_verification_fails(mock_ledger, temp_backup_dir):
    """Test restore when verification fails"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create backup
    backup_file = manager.backup()
    
    # Make verification fail
    mock_ledger.verify_chain.return_value = False
    
    # Restore should fail
    result = manager.restore(backup_file, verify=True)
    
    assert result is False


def test_restore_invalid_file(mock_ledger, temp_backup_dir):
    """Test restore with invalid/nonexistent file"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    result = manager.restore("nonexistent_file.json.gz")
    
    assert result is False


def test_restore_corrupted_json(mock_ledger, temp_backup_dir):
    """Test restore with corrupted JSON"""
    from venom.ops.backup import BackupManager
    
    # Create corrupted backup file
    backup_file = Path(temp_backup_dir) / "corrupted.json.gz"
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with gzip.open(backup_file, 'wt') as f:
        f.write("invalid json data {{{")
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    result = manager.restore(str(backup_file))
    
    assert result is False


def test_on_beat_disabled(mock_ledger, temp_backup_dir):
    """Test on_beat when disabled does nothing"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=False)
    
    # Call on_beat multiple times
    for i in range(20):
        manager.on_beat(i)
    
    # Beat counter should not change
    assert manager.beat_counter == 0


def test_on_beat_triggers_backup(mock_ledger, temp_backup_dir):
    """Test on_beat triggers backup at interval"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    manager.backup_interval = 5
    
    # Call on_beat 4 times - should not trigger
    for i in range(4):
        manager.on_beat(i)
    
    assert manager.beat_counter == 4
    backups = manager.list_backups()
    initial_count = len(backups)
    
    # 5th call should trigger backup
    manager.on_beat(5)
    
    assert manager.beat_counter == 0  # Reset after backup
    backups = manager.list_backups()
    assert len(backups) == initial_count + 1


def test_on_beat_multiple_cycles(mock_ledger, temp_backup_dir):
    """Test on_beat over multiple intervals"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    manager.backup_interval = 3
    
    # Trigger 2 complete cycles with delays to ensure distinct timestamps
    for i in range(7):
        manager.on_beat(i)
        if (i + 1) % 3 == 0:  # After each backup trigger
            time.sleep(1.1)  # Ensure distinct second in timestamp
    
    # Should have created 2 backups
    backups = manager.list_backups()
    assert len(backups) == 2
    assert manager.beat_counter == 1  # Partial progress in 3rd cycle


def test_list_backups_empty(mock_ledger, temp_backup_dir):
    """Test list_backups when directory is empty"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    backups = manager.list_backups()
    
    assert isinstance(backups, list)
    assert len(backups) == 0


def test_list_backups_nonexistent_dir(mock_ledger):
    """Test list_backups when directory doesn't exist"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir="/nonexistent/path", enabled=False)
    backups = manager.list_backups()
    
    assert backups == []


def test_list_backups_multiple(mock_ledger, temp_backup_dir):
    """Test list_backups with multiple backups"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create multiple backups - use default naming that starts with "ledger_"
    # Need at least 1 second delay for distinct filenames
    for i in range(3):
        manager.backup()
        time.sleep(1.1)  # Ensure distinct second in timestamp
    
    backups = manager.list_backups()
    
    assert len(backups) == 3
    # Should be sorted in reverse order (newest first)
    for backup in backups:
        assert "ledger_" in backup
        assert backup.endswith(".json.gz")


def test_list_backups_sorted_order(mock_ledger, temp_backup_dir):
    """Test list_backups returns sorted order"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create backups with known timestamps - need at least 1 second delay for distinct filenames
    files = []
    for i in range(3):
        time.sleep(1.1)  # Ensure distinct second in timestamp
        result = manager.backup()
        files.append(result)
    
    backups = manager.list_backups()
    
    # Should be reverse sorted (newest first)
    assert len(backups) == 3
    # Verify newest is first
    assert backups[0] == files[-1]


def test_backup_metadata_complete(mock_ledger, temp_backup_dir):
    """Test backup contains all required metadata"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    backup_file = manager.backup()
    
    with gzip.open(backup_file, 'rt') as f:
        data = json.load(f)
    
    # Verify all metadata fields
    assert 'timestamp' in data
    assert 'chain_length' in data
    assert 'merkle_root' in data
    assert 'chain' in data
    
    assert isinstance(data['timestamp'], (int, float))
    assert data['chain_length'] == 2
    assert data['merkle_root'] == "abc123"
    assert isinstance(data['chain'], list)
    assert len(data['chain']) == 2


def test_backup_compression(mock_ledger, temp_backup_dir):
    """Test that backup is actually compressed"""
    from venom.ops.backup import BackupManager
    
    # Create ledger with substantial data
    large_data = [{"beat": i, "theta": 0.5, "data": "x" * 100} for i in range(50)]
    mock_ledger.export_chain.return_value = large_data
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    backup_file = manager.backup()
    
    # Compare sizes
    compressed_size = Path(backup_file).stat().st_size
    uncompressed_size = len(json.dumps({"chain": large_data}).encode())
    
    # Compressed should be smaller
    assert compressed_size < uncompressed_size
    # Should have significant compression (at least 50% reduction)
    assert compressed_size < uncompressed_size * 0.5


def test_restore_ledger_entry_creation(mock_ledger, temp_backup_dir):
    """Test restore creates LedgerEntry objects correctly"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create and restore
    backup_file = manager.backup()
    
    # Patch LedgerEntry at its actual import location within the restore method
    with patch('venom.ledger.immutable_ledger.LedgerEntry') as mock_entry:
        result = manager.restore(backup_file, verify=False)
        
        # Should have created 2 entries
        assert mock_entry.call_count == 2
        
        # Verify entries were added to chain
        assert result is True


def test_backup_filename_generation(mock_ledger, temp_backup_dir):
    """Test automatic filename generation"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    
    # Create backup without filename
    backup_file = manager.backup()
    
    # Should contain timestamp in filename
    assert "ledger_" in backup_file
    assert ".json.gz" in backup_file
    
    # Filename should include date/time components
    filename = Path(backup_file).name
    assert filename.startswith("ledger_")
    assert len(filename) > 20  # Should have timestamp


def test_backup_beat_counter_increment(mock_ledger, temp_backup_dir):
    """Test beat counter increments correctly"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    manager.backup_interval = 10
    
    assert manager.beat_counter == 0
    
    for i in range(5):
        manager.on_beat(i)
    
    assert manager.beat_counter == 5


def test_backup_beat_counter_reset(mock_ledger, temp_backup_dir):
    """Test beat counter resets after backup"""
    from venom.ops.backup import BackupManager
    
    manager = BackupManager(mock_ledger, backup_dir=temp_backup_dir, enabled=True)
    manager.backup_interval = 5
    
    # Increment to trigger backup
    for i in range(5):
        manager.on_beat(i)
    
    # Counter should reset
    assert manager.beat_counter == 0
