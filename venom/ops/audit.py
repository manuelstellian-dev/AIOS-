"""
Audit Trail Module
Structured logging for all cycle phases: Detect, Predict, Decide, Act, Log, Learn, Sync
"""
import json
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditTrail:
    """
    Structured audit logging for VENOM cycle phases
    
    Phases:
    - Detect: Anomaly detection
    - Predict: Entropy inference
    - Decide: Action determination
    - Act: Action execution
    - Log: Ledger recording
    - Learn: Weight adjustment (PID)
    - Sync: P2P synchronization
    """
    
    def __init__(self, enabled: bool = False, audit_file: Optional[str] = None):
        """
        Initialize audit trail
        
        Args:
            enabled: Enable audit logging
            audit_file: Path to audit log file (JSON Lines format)
        """
        self.enabled = enabled
        self.audit_file = audit_file
        
        if self.enabled and self.audit_file:
            # Create audit file if it doesn't exist
            Path(self.audit_file).parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Audit trail enabled: {self.audit_file}")
    
    def _log_event(self, phase: str, data: Dict[str, Any]):
        """
        Log an audit event
        
        Args:
            phase: Cycle phase name
            data: Event data
        """
        if not self.enabled:
            return
        
        event = {
            "timestamp": time.time(),
            "phase": phase,
            "data": data
        }
        
        # Log to file if specified
        if self.audit_file:
            try:
                with open(self.audit_file, 'a') as f:
                    f.write(json.dumps(event) + '\n')
            except Exception as e:
                logger.error(f"Failed to write audit event: {e}")
        
        # Also log to standard logger
        logger.info(f"AUDIT [{phase}]: {json.dumps(data)}")
    
    def detect(self, features: Dict[str, Any], anomalies: int):
        """
        Log Detect phase (anomaly detection)
        
        Args:
            features: Input features
            anomalies: Number of anomalies detected
        """
        self._log_event("DETECT", {
            "features": features,
            "anomalies_detected": anomalies
        })
    
    def predict(self, threat_score: float, entropy_data: Dict[str, Any]):
        """
        Log Predict phase (entropy inference)
        
        Args:
            threat_score: Predicted threat score
            entropy_data: Entropy model data
        """
        self._log_event("PREDICT", {
            "threat_score": threat_score,
            "entropy_data": entropy_data
        })
    
    def decide(self, decvec: Dict[str, Any], action: str):
        """
        Log Decide phase (action determination)
        
        Args:
            decvec: Decision vector
            action: Determined action
        """
        self._log_event("DECIDE", {
            "decision_vector": decvec,
            "action": action
        })
    
    def act(self, action: str, success: bool, details: Optional[Dict[str, Any]] = None):
        """
        Log Act phase (action execution)
        
        Args:
            action: Action executed
            success: Whether action succeeded
            details: Optional action details
        """
        self._log_event("ACT", {
            "action": action,
            "success": success,
            "details": details or {}
        })
    
    def log_entry(self, entry_hash: str, entry_type: str):
        """
        Log Log phase (ledger recording)
        
        Args:
            entry_hash: Hash of ledger entry
            entry_type: Type of entry
        """
        self._log_event("LOG", {
            "entry_hash": entry_hash,
            "entry_type": entry_type
        })
    
    def learn(self, weights_before: Dict[str, float], weights_after: Dict[str, float], 
              pid_output: float):
        """
        Log Learn phase (weight adjustment)
        
        Args:
            weights_before: Genome weights before adjustment
            weights_after: Genome weights after adjustment
            pid_output: PID controller output
        """
        self._log_event("LEARN", {
            "weights_before": weights_before,
            "weights_after": weights_after,
            "pid_output": pid_output
        })
    
    def sync(self, peers: int, messages_sent: int, messages_received: int):
        """
        Log Sync phase (P2P synchronization)
        
        Args:
            peers: Number of connected peers
            messages_sent: Messages sent to peers
            messages_received: Messages received from peers
        """
        self._log_event("SYNC", {
            "peers_connected": peers,
            "messages_sent": messages_sent,
            "messages_received": messages_received
        })
    
    def beat_summary(self, beat: int, summary: Dict[str, Any]):
        """
        Log complete beat summary
        
        Args:
            beat: Beat number
            summary: Beat execution summary
        """
        self._log_event("BEAT_SUMMARY", {
            "beat": beat,
            "summary": summary
        })
