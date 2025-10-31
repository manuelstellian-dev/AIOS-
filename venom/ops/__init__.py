"""
Operations module for VENOM Λ-GENESIS
Includes backup/restore, audit trails, and operational utilities
"""

from .backup import BackupManager
from .audit import AuditTrail

__all__ = ['BackupManager', 'AuditTrail']
