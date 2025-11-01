"""
Tests for Security Audit Logger
"""
import pytest
import json
from datetime import datetime, timedelta, timezone
from venom.security.audit import AuditLogger


def test_log_event(tmp_path):
    """Test logging security events"""
    log_file = tmp_path / "audit.log"
    audit = AuditLogger(str(log_file))
    
    # Log an event
    event_id = audit.log_event(
        event_type='auth',
        user='admin',
        action='login',
        resource='web_portal',
        status='success',
        metadata={'ip': '192.168.1.1'}
    )
    
    # Verify event ID was returned
    assert event_id is not None
    assert len(event_id) == 36  # UUID format
    
    # Verify log file was created
    assert log_file.exists()
    
    # Read and verify event
    with open(log_file, 'r') as f:
        line = f.readline()
        event = json.loads(line)
    
    assert event['event_id'] == event_id
    assert event['event_type'] == 'auth'
    assert event['user'] == 'admin'
    assert event['action'] == 'login'
    assert event['resource'] == 'web_portal'
    assert event['status'] == 'success'
    assert event['metadata']['ip'] == '192.168.1.1'
    assert 'timestamp' in event
    assert 'hash' in event


def test_get_events_filtered(tmp_path):
    """Test querying events with filters"""
    log_file = tmp_path / "audit.log"
    audit = AuditLogger(str(log_file))
    
    # Log multiple events
    audit.log_event('auth', 'alice', 'login', status='success')
    audit.log_event('auth', 'bob', 'login', status='failure')
    audit.log_event('access', 'alice', 'read_file', resource='secrets.txt', status='success')
    audit.log_event('config', 'admin', 'update_config', status='success')
    
    # Get all events
    all_events = audit.get_events()
    assert len(all_events) == 4
    
    # Filter by user
    alice_events = audit.get_events(user='alice')
    assert len(alice_events) == 2
    assert all(e['user'] == 'alice' for e in alice_events)
    
    # Filter by event type
    auth_events = audit.get_events(event_type='auth')
    assert len(auth_events) == 2
    assert all(e['event_type'] == 'auth' for e in auth_events)
    
    # Filter by time range
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1)
    future = now + timedelta(hours=1)
    
    recent_events = audit.get_events(start_time=past, end_time=future)
    assert len(recent_events) == 4


def test_integrity_verification(tmp_path):
    """Test audit log integrity verification"""
    log_file = tmp_path / "audit.log"
    audit = AuditLogger(str(log_file))
    
    # Log events
    audit.log_event('auth', 'user1', 'action1')
    audit.log_event('auth', 'user2', 'action2')
    audit.log_event('auth', 'user3', 'action3')
    
    # Verify integrity
    assert audit.verify_integrity()
    
    # Empty log should also verify
    empty_log_file = tmp_path / "empty_audit.log"
    empty_audit = AuditLogger(str(empty_log_file))
    assert empty_audit.verify_integrity()


def test_tamper_detection(tmp_path):
    """Test detection of tampered audit logs"""
    log_file = tmp_path / "audit.log"
    audit = AuditLogger(str(log_file))
    
    # Log events
    audit.log_event('auth', 'user1', 'action1')
    audit.log_event('auth', 'user2', 'action2')
    audit.log_event('auth', 'user3', 'action3')
    
    # Verify integrity before tampering
    assert audit.verify_integrity()
    
    # Tamper with log file (modify an event)
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Modify the second event
    if len(lines) > 1:
        event = json.loads(lines[1])
        event['action'] = 'tampered_action'
        lines[1] = json.dumps(event) + '\n'
        
        with open(log_file, 'w') as f:
            f.writelines(lines)
    
    # Verify integrity should fail
    assert not audit.verify_integrity()


def test_export_events(tmp_path):
    """Test exporting audit events to JSON and CSV"""
    log_file = tmp_path / "audit.log"
    audit = AuditLogger(str(log_file))
    
    # Log events
    audit.log_event('auth', 'user1', 'login', status='success')
    audit.log_event('access', 'user2', 'read_file', resource='data.txt', status='success')
    
    # Export to JSON
    json_file = tmp_path / "audit_export.json"
    audit.export_events(str(json_file), format='json')
    
    # Verify JSON export
    assert json_file.exists()
    with open(json_file, 'r') as f:
        exported = json.load(f)
    assert len(exported) == 2
    assert exported[0]['user'] == 'user1'
    assert exported[1]['user'] == 'user2'
    
    # Export to CSV
    csv_file = tmp_path / "audit_export.csv"
    audit.export_events(str(csv_file), format='csv')
    
    # Verify CSV export
    assert csv_file.exists()
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    assert len(lines) == 3  # Header + 2 events
    assert 'event_id' in lines[0]
    assert 'user1' in lines[1]
    assert 'user2' in lines[2]
