"""
VENOM Λ-GENESIS - Fractal Organism Architecture
Orchestrated by Arbiter with 4 parallel flows (R, B, E, O)

Architecture:
- Arbiter: Decisional brain with parallel orchestration (ThreadPoolExecutor)
- T_Λ Pulse: Time compression synchronization
- Genomic PID: Stability controller (ΔV < 0)
- 4 Cores: RegenCore(R), BalanceCore(B), EntropyCore(E), OptimizeCore(O)
- Entropy Model: Torch Linear(1,1) + Sigmoid
- Immutable Ledger: SHA3-256 blockchain with Merkle root
- P2P Mesh: Nanobot Phalanx with adaptive FIFO delivery
- Observability: Prometheus metrics, health checks, monitoring
- Operations: Backup/restore, graceful shutdown, audit trails
- Security: Ed25519 signing, JWT authentication
"""

__version__ = "0.2.0"

from .core.arbiter import Arbiter, Action
from .core.constants import Constants
from .flows.parallel_flows import RegenCore, BalanceCore, EntropyCore, OptimizeCore
from .flows.parallel_flows import RFlow, BFlow, EFlow, OFlow  # Aliases
from .sync.pulse import TLambdaPulse
from .control.genomic_pid import GenomicPID
from .inference.entropy_model import EntropyModel
from .ledger.immutable_ledger import ImmutableLedger, LedgerEntry
from .mesh.p2p import P2PMesh
from .observability import MetricsCollector, MetricsServer, HealthChecker
from .ops import BackupManager, AuditTrail
from .security import LedgerSigner, MeshAuthenticator

__all__ = [
    "Arbiter",
    "Action",
    "Constants",
    "RegenCore",
    "BalanceCore",
    "EntropyCore",
    "OptimizeCore",
    "RFlow",
    "BFlow", 
    "EFlow",
    "OFlow",
    "TLambdaPulse",
    "GenomicPID",
    "EntropyModel",
    "ImmutableLedger",
    "LedgerEntry",
    "P2PMesh",
    "MetricsCollector",
    "MetricsServer",
    "HealthChecker",
    "BackupManager",
    "AuditTrail",
    "LedgerSigner",
    "MeshAuthenticator",
]
