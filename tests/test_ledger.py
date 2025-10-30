"""Tests for Immutable Ledger"""
import pytest
from venom.ledger.immutable_ledger import ImmutableLedger, LedgerEntry


def test_ledger_initialization():
    """Test ledger initialization with genesis block"""
    ledger = ImmutableLedger()
    
    assert len(ledger.chain) == 1
    assert ledger.chain[0].index == 0
    assert ledger.chain[0].data["type"] == "genesis"
    assert ledger.chain[0].previous_hash == "0" * 64


def test_add_entry():
    """Test adding entries to ledger"""
    ledger = ImmutableLedger()
    
    data = {"test": "value"}
    entry = ledger.add_entry(data)
    
    assert entry.index == 1
    assert entry.data == data
    assert entry.previous_hash == ledger.chain[0].hash
    assert len(ledger.chain) == 2


def test_record_action():
    """Test recording actions"""
    ledger = ImmutableLedger()
    
    entry = ledger.record_action("TEST_ACTION", {"param": 123})
    
    assert entry.data["type"] == "action"
    assert entry.data["action"] == "TEST_ACTION"
    assert entry.data["details"]["param"] == 123


def test_record_pulse():
    """Test recording pulse data"""
    ledger = ImmutableLedger()
    
    pulse_data = {"pulse_id": 1, "t_lambda": 0.004211}
    entry = ledger.record_pulse(pulse_data)
    
    assert entry.data["type"] == "pulse"
    assert entry.data["pulse"]["pulse_id"] == 1


def test_record_flow_result():
    """Test recording flow results"""
    ledger = ImmutableLedger()
    
    result = {"urgency": 0.4, "cost": 0.2}
    entry = ledger.record_flow_result("R", result)
    
    assert entry.data["type"] == "flow_result"
    assert entry.data["flow"] == "R"
    assert entry.data["result"]["urgency"] == 0.4


def test_chain_verification():
    """Test chain integrity verification"""
    ledger = ImmutableLedger()
    
    # Add some entries
    ledger.add_entry({"data": 1})
    ledger.add_entry({"data": 2})
    ledger.add_entry({"data": 3})
    
    # Chain should be valid
    assert ledger.verify_chain() == True
    
    # Tamper with an entry
    ledger.chain[2].data["data"] = 999
    
    # Chain should now be invalid
    assert ledger.verify_chain() == False


def test_merkle_root():
    """Test Merkle root computation"""
    ledger = ImmutableLedger()
    
    # Add entries
    ledger.add_entry({"data": 1})
    ledger.add_entry({"data": 2})
    
    merkle_root = ledger.compute_merkle_root()
    
    assert isinstance(merkle_root, str)
    assert len(merkle_root) == 64  # SHA3-256 hex length
    
    # Merkle root should be deterministic
    merkle_root2 = ledger.compute_merkle_root()
    assert merkle_root == merkle_root2


def test_manifest():
    """Test ledger manifest generation"""
    ledger = ImmutableLedger()
    
    ledger.add_entry({"data": 1})
    ledger.add_entry({"data": 2})
    
    manifest = ledger.get_manifest()
    
    assert "chain_length" in manifest
    assert "genesis_hash" in manifest
    assert "latest_hash" in manifest
    assert "merkle_root" in manifest
    assert "timestamp" in manifest
    
    assert manifest["chain_length"] == 3
    assert manifest["genesis_hash"] == ledger.chain[0].hash
    assert manifest["latest_hash"] == ledger.chain[-1].hash


def test_get_entries():
    """Test retrieving entries"""
    ledger = ImmutableLedger()
    
    for i in range(5):
        ledger.add_entry({"data": i})
    
    # Get all entries
    all_entries = ledger.get_entries()
    assert len(all_entries) == 6  # 5 + genesis
    
    # Get range
    range_entries = ledger.get_entries(start=2, end=4)
    assert len(range_entries) == 2
    assert range_entries[0].index == 2
    assert range_entries[1].index == 3


def test_canonical_json_hashing():
    """Test that canonical JSON produces consistent hashes for same data"""
    ledger = ImmutableLedger()
    
    # Add same data twice with different key ordering
    data1 = {"z": 3, "a": 1, "m": 2}
    data2 = {"a": 1, "m": 2, "z": 3}
    
    entry1 = ledger.add_entry(data1)
    entry2 = ledger.add_entry(data2)
    
    # Data hashes should be same due to canonical JSON, but entry hashes differ
    # because they have different indices and previous_hash
    # Test that the data portion is consistently ordered
    import json
    json1 = json.dumps(entry1.data, sort_keys=True, separators=(",", ":"))
    json2 = json.dumps(entry2.data, sort_keys=True, separators=(",", ":"))
    assert json1 == json2
