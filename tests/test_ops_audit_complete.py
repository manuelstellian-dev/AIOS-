"""
Complete comprehensive tests for venom/ops/audit.py to achieve 97%+ coverage
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open


@pytest.fixture
def temp_audit_file():
    """Create temporary audit file"""
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except:
        pass


def test_audit_trail_init_disabled():
    """Test initialization with disabled=False"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=False)
    
    assert audit.enabled is False
    assert audit.audit_file is None


def test_audit_trail_init_enabled_no_file():
    """Test initialization enabled without file"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=None)
    
    assert audit.enabled is True
    assert audit.audit_file is None


def test_audit_trail_init_enabled_with_file(temp_audit_file):
    """Test initialization with enabled and file"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    assert audit.enabled is True
    assert audit.audit_file == temp_audit_file
    assert Path(temp_audit_file).exists()


def test_audit_trail_init_creates_parent_dirs():
    """Test initialization creates parent directories"""
    from venom.ops.audit import AuditTrail
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = os.path.join(tmpdir, "subdir", "audit.jsonl")
        
        audit = AuditTrail(enabled=True, audit_file=audit_file)
        
        assert Path(audit_file).parent.exists()


def test_log_event_disabled():
    """Test _log_event when disabled does nothing"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=False)
    
    # Should not raise any exceptions
    audit._log_event("TEST", {"key": "value"})


def test_log_event_enabled_no_file():
    """Test _log_event enabled without file (logs to logger only)"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=None)
    
    with patch('venom.ops.audit.logger') as mock_logger:
        audit._log_event("TEST", {"key": "value"})
        
        # Should log to logger
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "TEST" in call_args
        assert "key" in call_args


def test_log_event_enabled_with_file(temp_audit_file):
    """Test _log_event writes to file"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit._log_event("TEST_PHASE", {"test_key": "test_value"})
    
    # Read file and verify
    with open(temp_audit_file, 'r') as f:
        line = f.readline()
        event = json.loads(line)
        
        assert event['phase'] == "TEST_PHASE"
        assert event['data']['test_key'] == "test_value"
        assert 'timestamp' in event


def test_log_event_multiple_events(temp_audit_file):
    """Test logging multiple events"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit._log_event("PHASE1", {"data": 1})
    audit._log_event("PHASE2", {"data": 2})
    audit._log_event("PHASE3", {"data": 3})
    
    # Verify all events written
    with open(temp_audit_file, 'r') as f:
        lines = f.readlines()
        
    assert len(lines) == 3
    
    events = [json.loads(line) for line in lines]
    assert events[0]['phase'] == "PHASE1"
    assert events[1]['phase'] == "PHASE2"
    assert events[2]['phase'] == "PHASE3"


def test_log_event_file_error_handling(temp_audit_file):
    """Test _log_event handles file write errors"""
    from venom.ops.audit import AuditTrail
    
    # Mock Path.mkdir to avoid permission error during init
    with patch('venom.ops.audit.Path') as mock_path:
        mock_path.return_value.parent.mkdir = Mock()
        audit = AuditTrail(enabled=True, audit_file="/invalid/path/audit.jsonl")
    
    # Should not raise exception, just log error when trying to write
    with patch('venom.ops.audit.logger') as mock_logger:
        with patch('builtins.open', side_effect=PermissionError("No permission")):
            audit._log_event("TEST", {"data": "value"})
            
            # Should log error
            assert mock_logger.error.called


def test_detect_phase(temp_audit_file):
    """Test detect phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    features = {"cpu": 50, "memory": 70}
    audit.detect(features, anomalies=3)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "DETECT"
    assert event['data']['features'] == features
    assert event['data']['anomalies_detected'] == 3


def test_predict_phase(temp_audit_file):
    """Test predict phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    entropy_data = {"entropy": 0.75, "confidence": 0.9}
    audit.predict(threat_score=0.85, entropy_data=entropy_data)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "PREDICT"
    assert event['data']['threat_score'] == 0.85
    assert event['data']['entropy_data'] == entropy_data


def test_decide_phase(temp_audit_file):
    """Test decide phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    decvec = {"option_a": 0.3, "option_b": 0.7}
    audit.decide(decvec, action="option_b")
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "DECIDE"
    assert event['data']['decision_vector'] == decvec
    assert event['data']['action'] == "option_b"


def test_act_phase_success(temp_audit_file):
    """Test act phase logging with success"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    details = {"resource": "server1", "duration": 5.2}
    audit.act(action="restart", success=True, details=details)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "ACT"
    assert event['data']['action'] == "restart"
    assert event['data']['success'] is True
    assert event['data']['details'] == details


def test_act_phase_failure(temp_audit_file):
    """Test act phase logging with failure"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit.act(action="deploy", success=False, details={"error": "timeout"})
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['data']['success'] is False
    assert event['data']['details']['error'] == "timeout"


def test_act_phase_no_details(temp_audit_file):
    """Test act phase logging without details"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit.act(action="test", success=True)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['data']['details'] == {}


def test_log_entry_phase(temp_audit_file):
    """Test log entry phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit.log_entry(entry_hash="abc123def456", entry_type="action")
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "LOG"
    assert event['data']['entry_hash'] == "abc123def456"
    assert event['data']['entry_type'] == "action"


def test_learn_phase(temp_audit_file):
    """Test learn phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    weights_before = {"w1": 0.5, "w2": 0.3}
    weights_after = {"w1": 0.6, "w2": 0.4}
    audit.learn(weights_before, weights_after, pid_output=0.1)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "LEARN"
    assert event['data']['weights_before'] == weights_before
    assert event['data']['weights_after'] == weights_after
    assert event['data']['pid_output'] == 0.1


def test_sync_phase(temp_audit_file):
    """Test sync phase logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    audit.sync(peers=5, messages_sent=10, messages_received=8)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "SYNC"
    assert event['data']['peers_connected'] == 5
    assert event['data']['messages_sent'] == 10
    assert event['data']['messages_received'] == 8


def test_beat_summary_phase(temp_audit_file):
    """Test beat summary logging"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    summary = {
        "duration": 1.5,
        "actions": 3,
        "anomalies": 1,
        "theta": 0.75
    }
    audit.beat_summary(beat=100, summary=summary)
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert event['phase'] == "BEAT_SUMMARY"
    assert event['data']['beat'] == 100
    assert event['data']['summary'] == summary


def test_all_phases_disabled():
    """Test all phase methods when disabled"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=False)
    
    # None of these should raise exceptions or write anything
    audit.detect({}, 0)
    audit.predict(0.5, {})
    audit.decide({}, "action")
    audit.act("action", True)
    audit.log_entry("hash", "type")
    audit.learn({}, {}, 0.1)
    audit.sync(0, 0, 0)
    audit.beat_summary(1, {})


def test_complete_cycle_logging(temp_audit_file):
    """Test logging a complete VENOM cycle"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    # Complete cycle
    audit.detect({"cpu": 50}, anomalies=1)
    audit.predict(0.7, {"entropy": 0.8})
    audit.decide({"action_a": 0.3, "action_b": 0.7}, "action_b")
    audit.act("action_b", True, {"duration": 2.5})
    audit.log_entry("hash123", "action")
    audit.learn({"w1": 0.5}, {"w1": 0.6}, 0.1)
    audit.sync(3, 5, 4)
    audit.beat_summary(1, {"duration": 10.0})
    
    # Verify all events logged
    with open(temp_audit_file, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 8
    
    phases = [json.loads(line)['phase'] for line in lines]
    assert phases == ["DETECT", "PREDICT", "DECIDE", "ACT", "LOG", "LEARN", "SYNC", "BEAT_SUMMARY"]


def test_event_timestamps(temp_audit_file):
    """Test that events have valid timestamps"""
    from venom.ops.audit import AuditTrail
    import time
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    before = time.time()
    audit.detect({}, 0)
    after = time.time()
    
    with open(temp_audit_file, 'r') as f:
        event = json.loads(f.readline())
    
    assert 'timestamp' in event
    assert before <= event['timestamp'] <= after


def test_json_serializable_data(temp_audit_file):
    """Test that all logged data is JSON serializable"""
    from venom.ops.audit import AuditTrail
    
    audit = AuditTrail(enabled=True, audit_file=temp_audit_file)
    
    # Test with various data types
    audit.detect({"int": 1, "float": 1.5, "str": "test", "bool": True, "null": None}, 0)
    audit.predict(0.5, {"list": [1, 2, 3], "dict": {"nested": "value"}})
    
    # Verify all events are valid JSON
    with open(temp_audit_file, 'r') as f:
        for line in f:
            event = json.loads(line)  # Should not raise
            assert 'timestamp' in event
            assert 'phase' in event
            assert 'data' in event
