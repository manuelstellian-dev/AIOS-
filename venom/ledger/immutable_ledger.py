"""
Immutable Ledger - SHA3-based blockchain for action recording
All actions are recorded immutably with cryptographic hashing
"""
import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class LedgerEntry:
    """Single entry in the immutable ledger"""
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary"""
        return asdict(self)


class ImmutableLedger:
    """
    Immutable ledger using SHA3-256 hashing
    Records all system actions in a blockchain-like structure
    """
    
    def __init__(self):
        """Initialize immutable ledger with genesis block"""
        self.chain: List[LedgerEntry] = []
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        """Create the genesis (first) block"""
        genesis_data = {
            "type": "genesis",
            "message": "VENOM Λ-GENESIS initialization",
            "version": "0.1.0"
        }
        genesis_entry = self._create_entry(genesis_data, "0" * 64)
        self.chain.append(genesis_entry)
        
    def _calculate_hash(self, index: int, timestamp: float, 
                       data: Dict[str, Any], previous_hash: str) -> str:
        """
        Calculate SHA3-256 hash for a ledger entry
        
        Args:
            index: Entry index
            timestamp: Entry timestamp
            data: Entry data
            previous_hash: Hash of previous entry
            
        Returns:
            SHA3-256 hash as hex string
        """
        # Create deterministic string representation
        entry_string = json.dumps({
            "index": index,
            "timestamp": timestamp,
            "data": data,
            "previous_hash": previous_hash
        }, sort_keys=True)
        
        # Calculate SHA3-256
        return hashlib.sha3_256(entry_string.encode()).hexdigest()
    
    def _create_entry(self, data: Dict[str, Any], previous_hash: str) -> LedgerEntry:
        """
        Create a new ledger entry
        
        Args:
            data: Entry data
            previous_hash: Hash of previous entry
            
        Returns:
            New LedgerEntry
        """
        index = len(self.chain)
        timestamp = time.time()
        entry_hash = self._calculate_hash(index, timestamp, data, previous_hash)
        
        return LedgerEntry(
            index=index,
            timestamp=timestamp,
            data=data,
            previous_hash=previous_hash,
            hash=entry_hash
        )
    
    def add_entry(self, data: Dict[str, Any]) -> LedgerEntry:
        """
        Add new entry to the ledger
        
        Args:
            data: Data to record
            
        Returns:
            Created ledger entry
        """
        previous_entry = self.chain[-1]
        new_entry = self._create_entry(data, previous_entry.hash)
        self.chain.append(new_entry)
        return new_entry
    
    def record_action(self, action_type: str, details: Dict[str, Any]) -> LedgerEntry:
        """
        Record an action in the ledger
        
        Args:
            action_type: Type of action
            details: Action details
            
        Returns:
            Created ledger entry
        """
        data = {
            "type": "action",
            "action": action_type,
            "details": details
        }
        return self.add_entry(data)
    
    def record_pulse(self, pulse_data: Dict[str, Any]) -> LedgerEntry:
        """
        Record a T_Λ pulse in the ledger
        
        Args:
            pulse_data: Pulse data
            
        Returns:
            Created ledger entry
        """
        data = {
            "type": "pulse",
            "pulse": pulse_data
        }
        return self.add_entry(data)
    
    def record_flow_result(self, flow_name: str, result: Dict[str, Any]) -> LedgerEntry:
        """
        Record a flow execution result
        
        Args:
            flow_name: Name of the flow
            result: Flow execution result
            
        Returns:
            Created ledger entry
        """
        data = {
            "type": "flow_result",
            "flow": flow_name,
            "result": result
        }
        return self.add_entry(data)
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire chain
        
        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Verify hash
            calculated_hash = self._calculate_hash(
                current.index,
                current.timestamp,
                current.data,
                current.previous_hash
            )
            
            if calculated_hash != current.hash:
                return False
                
            # Verify chain linkage
            if current.previous_hash != previous.hash:
                return False
                
        return True
    
    def get_entries(self, start: int = 0, end: Optional[int] = None) -> List[LedgerEntry]:
        """
        Get entries from the ledger
        
        Args:
            start: Start index
            end: End index (None for all)
            
        Returns:
            List of ledger entries
        """
        if end is None:
            return self.chain[start:]
        return self.chain[start:end]
    
    def get_latest_entry(self) -> LedgerEntry:
        """Get the latest entry in the ledger"""
        return self.chain[-1]
    
    def get_chain_length(self) -> int:
        """Get the length of the chain"""
        return len(self.chain)
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """
        Export the entire chain as a list of dictionaries
        
        Returns:
            List of entry dictionaries
        """
        return [entry.to_dict() for entry in self.chain]
