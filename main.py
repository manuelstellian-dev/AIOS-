#!/usr/bin/env python3
"""
VENOM Λ-GENESIS Main Entry Point
Fractal organism with Arbiter orchestration
"""
import argparse
import logging
import sys

from venom import (
    Arbiter,
    TLambdaPulse,
    GenomicPID,
    EntropyModel,
    ImmutableLedger,
    P2PMesh
)
from venom.ops.backup import BackupManager
from venom.ops.shutdown import GracefulShutdown
from venom.ops.audit import AuditTrail
from venom.security.signing import LedgerSigner
from venom.security.auth import MeshAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for VENOM Λ-GENESIS"""
    parser = argparse.ArgumentParser(description='VENOM Λ-GENESIS Fractal Organism')
    parser.add_argument('--beats', type=int, default=10, 
                       help='Number of beats to execute (-1 for infinite)')
    parser.add_argument('--k-flows', type=int, default=4,
                       help='Number of parallel flows')
    parser.add_argument('--p-nodes', type=int, default=5,
                       help='Number of initial nodes')
    parser.add_argument('--t1', type=float, default=0.001,
                       help='Base time T1')
    parser.add_argument('--t-threshold', type=float, default=0.02,
                       help='Time threshold for PID')
    parser.add_argument('--mesh', action='store_true',
                       help='Enable P2P mesh networking')
    parser.add_argument('--mesh-port', type=int, default=9000,
                       help='P2P mesh port')
    
    # Stage 1 features
    parser.add_argument('--enable-backup', action='store_true',
                       help='Enable automatic ledger backups')
    parser.add_argument('--backup-dir', type=str, default='./backups',
                       help='Backup directory')
    parser.add_argument('--sign-ledger', action='store_true',
                       help='Enable Ed25519 ledger signing')
    parser.add_argument('--mesh-auth', action='store_true',
                       help='Enable JWT mesh authentication')
    parser.add_argument('--mesh-secret', type=str, default='venom-secret-key',
                       help='Secret key for mesh authentication')
    parser.add_argument('--audit-trail', action='store_true',
                       help='Enable structured audit logging')
    parser.add_argument('--audit-file', type=str, default='./audit.jsonl',
                       help='Audit log file')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("VENOM Λ-GENESIS - Fractal Organism")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  Beats: {args.beats}")
    logger.info(f"  k (flows): {args.k_flows}")
    logger.info(f"  P (nodes): {args.p_nodes}")
    logger.info(f"  T1: {args.t1}")
    logger.info(f"  T_threshold: {args.t_threshold}")
    logger.info(f"  Mesh enabled: {args.mesh}")
    logger.info(f"  Backup enabled: {args.enable_backup}")
    logger.info(f"  Ledger signing: {args.sign_ledger}")
    logger.info(f"  Mesh auth: {args.mesh_auth}")
    logger.info(f"  Audit trail: {args.audit_trail}")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        pulse = TLambdaPulse(
            k=args.k_flows,
            p=args.p_nodes,
            t1=args.t1
        )
        
        pid = GenomicPID(
            kp=0.6,
            ki=0.1,
            kd=0.05,
            t_threshold=args.t_threshold
        )
        
        entropy_model = EntropyModel(ml_weight=0.12)
        ledger = ImmutableLedger()
        
        mesh = None
        mesh_auth = None
        if args.mesh:
            mesh = P2PMesh(node_id="venom-node-1", port=args.mesh_port)
            mesh.start()
            logger.info(f"P2P Mesh started on port {mesh.port}")
            
            # Enable mesh authentication if requested
            if args.mesh_auth:
                mesh_auth = MeshAuthenticator(secret=args.mesh_secret)
                logger.info("Mesh authentication enabled")
        
        # Initialize Stage 1 features
        backup_mgr = BackupManager(ledger, backup_dir=args.backup_dir, enabled=args.enable_backup)
        
        signer = None
        if args.sign_ledger:
            signer = LedgerSigner()
            logger.info(f"Ledger signing enabled (public key: {signer.get_public_key_hex()[:16]}...)")
        
        audit = AuditTrail(enabled=args.audit_trail, audit_file=args.audit_file if args.audit_trail else None)
        
        # Create Arbiter
        arbiter = Arbiter(
            pulse=pulse,
            pid=pid,
            entropy_model=entropy_model,
            ledger=ledger,
            mesh=mesh
        )
        
        # Register graceful shutdown
        shutdown_handler = GracefulShutdown(arbiter)
        
        # Start execution
        logger.info("Starting Arbiter execution...")
        arbiter.start(beats=args.beats)
        
        # Final status
        status = arbiter.get_status()
        logger.info("=" * 60)
        logger.info("Final Status:")
        logger.info(f"  Total beats: {status['beat']}")
        logger.info(f"  PID stable: {status['pid_stable']}")
        logger.info(f"  Ledger length: {status['ledger_length']}")
        logger.info(f"  Ledger verified: {status['ledger_verified']}")
        logger.info(f"  Genome weights: {status['genome']['weights']}")
        logger.info("=" * 60)
        
        # Ledger manifest
        manifest = ledger.get_manifest()
        logger.info("Ledger Manifest:")
        logger.info(f"  Merkle Root: {manifest['merkle_root']}")
        logger.info(f"  Genesis Hash: {manifest['genesis_hash']}")
        logger.info(f"  Latest Hash: {manifest['latest_hash']}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
