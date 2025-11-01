"""
Security Audit Logger for VENOM
Provides tamper-evident logging with hash chains
"""
import csv
import json
import logging
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Security audit logger with tamper detection
    
    Features:
    - Structured JSON logging
    - Hash chain for tamper detection
    - Event filtering and querying
    - Export to JSON/CSV
    """
    
    def __init__(self, log_file: str = 'audit.log'):
        """
        Initialize audit logger
        
        Args:
            log_file: Path to audit log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.write_text("")
        
        logger.info(f"Audit logger initialized: {self.log_file}")
    
    def _hash_event(self, event: Dict, previous_hash: str = "") -> str:
        """
        Generate hash for event (includes previous hash for chaining)
        
        Args:
            event: Event dictionary
            previous_hash: Hash of previous event
            
        Returns:
            SHA-256 hash of event
        """
        # Create canonical representation
        event_str = json.dumps(event, sort_keys=True, separators=(",", ":"))
        
        # Include previous hash to create chain
        combined = previous_hash + event_str
        
        # Hash with SHA-256
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_last_event(self) -> Optional[Dict]:
        """
        Get the last event from log file
        
        Returns:
            Last event dictionary or None if log is empty
        """
        try:
            if self.log_file.stat().st_size == 0:
                return None
            
            # Read all events
            events = self._read_all_events()
            if events:
                return events[-1]
            return None
        except Exception as e:
            logger.warning(f"Failed to read last event: {e}")
            return None
    
    def _read_all_events(self) -> List[Dict]:
        """
        Read all events from log file
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read events: {e}")
        
        return events
    
    def log_event(
        self,
        event_type: str,
        user: str,
        action: str,
        resource: Optional[str] = None,
        status: str = 'success',
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log a security event
        
        Args:
            event_type: Type of event (e.g., 'auth', 'access', 'config')
            user: User performing action
            action: Action description
            resource: Resource affected (optional)
            status: Event status ('success' or 'failure')
            metadata: Additional metadata (optional)
            
        Returns:
            Event ID (UUID)
        """
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Get previous hash
        last_event = self._get_last_event()
        previous_hash = last_event.get('hash', '') if last_event else ''
        
        # Create event
        event = {
            'event_id': event_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': user,
            'action': action,
            'resource': resource,
            'status': status,
            'metadata': metadata or {},
            'previous_hash': previous_hash
        }
        
        # Calculate hash
        event['hash'] = self._hash_event(event, previous_hash)
        
        # Append to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
            
            logger.debug(f"Logged event {event_id}: {action}")
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            raise
        
        return event_id
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Query audit events with filters
        
        Args:
            start_time: Filter events after this time
            end_time: Filter events before this time
            user: Filter by user
            event_type: Filter by event type
            
        Returns:
            List of matching events
        """
        events = self._read_all_events()
        filtered = []
        
        for event in events:
            # Parse timestamp
            timestamp = datetime.fromisoformat(event['timestamp'])
            
            # Apply filters
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            if user and event.get('user') != user:
                continue
            if event_type and event.get('event_type') != event_type:
                continue
            
            filtered.append(event)
        
        return filtered
    
    def verify_integrity(self) -> bool:
        """
        Verify integrity of audit log (check hash chain)
        
        Returns:
            True if log is intact, False if tampered
        """
        events = self._read_all_events()
        
        if not events:
            logger.info("Audit log is empty")
            return True
        
        # Verify hash chain
        previous_hash = ''
        
        for i, event in enumerate(events):
            # Check previous hash matches
            if event.get('previous_hash') != previous_hash:
                logger.error(f"Hash chain broken at event {i}: previous_hash mismatch")
                return False
            
            # Recalculate hash
            stored_hash = event.get('hash')
            event_copy = {k: v for k, v in event.items() if k != 'hash'}
            calculated_hash = self._hash_event(event_copy, previous_hash)
            
            if stored_hash != calculated_hash:
                logger.error(f"Hash mismatch at event {i}: tampering detected")
                return False
            
            previous_hash = stored_hash
        
        logger.info(f"Audit log integrity verified ({len(events)} events)")
        return True
    
    def export_events(self, output_file: str, format: str = 'json') -> None:
        """
        Export audit events to file
        
        Args:
            output_file: Output file path
            format: Export format ('json' or 'csv')
        """
        events = self._read_all_events()
        output_path = Path(output_file)
        
        if format == 'json':
            # Export as JSON array
            with open(output_path, 'w') as f:
                json.dump(events, f, indent=2)
            logger.info(f"Exported {len(events)} events to {output_file} (JSON)")
        
        elif format == 'csv':
            # Export as CSV
            if not events:
                logger.warning("No events to export")
                return
            
            # Get all fields
            fields = ['event_id', 'timestamp', 'event_type', 'user', 'action', 
                     'resource', 'status', 'previous_hash', 'hash']
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                
                for event in events:
                    # Flatten metadata
                    row = {k: v for k, v in event.items() if k != 'metadata'}
                    writer.writerow(row)
            
            logger.info(f"Exported {len(events)} events to {output_file} (CSV)")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
