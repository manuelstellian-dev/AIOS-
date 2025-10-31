"""
Backup/Restore Module for Immutable Ledger
Provides compressed snapshot and recovery with verification
"""
import gzip
import json
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from ..ledger.immutable_ledger import ImmutableLedger

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manages ledger backup and restore operations
    
    Features:
    - Compressed snapshots (gzip)
    - Verification on restore
    - Automatic backup directory management
    """
    
    def __init__(self, ledger: ImmutableLedger, backup_dir: str = "./backups", enabled: bool = False):
        """
        Initialize backup manager
        
        Args:
            ledger: Immutable ledger instance
            backup_dir: Directory for backups
            enabled: Enable automatic backups
        """
        self.ledger = ledger
        self.backup_dir = Path(backup_dir)
        self.enabled = enabled
        self.backup_interval = 10  # Backup every N beats
        self.beat_counter = 0
        
        if self.enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Backup manager initialized: {self.backup_dir}")
    
    def backup(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Create a compressed backup of the ledger
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to backup file if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"ledger_{timestamp}.json.gz"
            
            backup_path = self.backup_dir / filename
            
            # Export ledger chain
            chain_data = self.ledger.export_chain()
            
            # Add metadata
            backup_data = {
                "timestamp": time.time(),
                "chain_length": len(chain_data),
                "merkle_root": self.ledger.compute_merkle_root(),
                "chain": chain_data
            }
            
            # Compress and save
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Ledger backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def restore(self, backup_path: str, verify: bool = True) -> bool:
        """
        Restore ledger from compressed backup
        
        Args:
            backup_path: Path to backup file
            verify: Verify chain integrity after restore
            
        Returns:
            True if restore successful, False otherwise
        """
        try:
            # Load compressed backup
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            chain_data = backup_data.get("chain", [])
            
            if not chain_data:
                logger.error("Backup contains no chain data")
                return False
            
            # Clear current ledger
            self.ledger.chain.clear()
            
            # Restore entries
            from ..ledger.immutable_ledger import LedgerEntry
            for entry_dict in chain_data:
                entry = LedgerEntry(**entry_dict)
                self.ledger.chain.append(entry)
            
            logger.info(f"Restored {len(chain_data)} entries from backup")
            
            # Verify if requested
            if verify:
                if not self.ledger.verify_chain():
                    logger.error("Restored chain failed verification")
                    return False
                logger.info("Restored chain verified successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def on_beat(self, beat_number: int):
        """
        Called on each beat to trigger automatic backup
        
        Args:
            beat_number: Current beat number
        """
        if not self.enabled:
            return
        
        self.beat_counter += 1
        
        if self.beat_counter >= self.backup_interval:
            self.backup()
            self.beat_counter = 0
    
    def list_backups(self):
        """List all available backups"""
        if not self.backup_dir.exists():
            return []
        
        backups = sorted(self.backup_dir.glob("ledger_*.json.gz"), reverse=True)
        return [str(b) for b in backups]
