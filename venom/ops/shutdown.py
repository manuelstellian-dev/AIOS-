"""
Graceful Shutdown Module
Handles SIGTERM/SIGINT signals with ordered component shutdown
"""
import signal
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Manages graceful shutdown of VENOM components
    
    Features:
    - Signal handlers for SIGTERM/SIGINT
    - Ordered shutdown: Pulse → Mesh → Ledger → Executor
    - Clean resource cleanup
    - Shutdown logging
    """
    
    def __init__(self, arbiter):
        """
        Initialize graceful shutdown handler
        
        Args:
            arbiter: Arbiter instance to shutdown
        """
        self.arbiter = arbiter
        self.shutdown_requested = False
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("Graceful shutdown handlers registered")
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        
        if self.shutdown_requested:
            logger.warning("Shutdown already in progress")
            return
        
        self.shutdown_requested = True
        self.shutdown()
    
    def shutdown(self):
        """Execute ordered shutdown sequence"""
        logger.info("=" * 60)
        logger.info("GRACEFUL SHUTDOWN SEQUENCE INITIATED")
        logger.info("=" * 60)
        
        try:
            # Step 1: Stop Arbiter execution
            logger.info("Step 1: Stopping Arbiter execution...")
            self.arbiter.running = False
            logger.info("✓ Arbiter stopped")
            
            # Step 2: Stop P2P Mesh
            if self.arbiter.mesh:
                logger.info("Step 2: Stopping P2P Mesh...")
                self.arbiter.mesh.stop()
                logger.info("✓ Mesh stopped")
            
            # Step 3: Finalize Ledger (optional final entry)
            logger.info("Step 3: Finalizing Ledger...")
            try:
                self.arbiter.ledger.record_action(
                    "SHUTDOWN",
                    {"reason": "graceful_shutdown", "beat": self.arbiter.beat_count}
                )
                manifest = self.arbiter.ledger.get_manifest()
                logger.info(f"✓ Ledger finalized (Merkle Root: {manifest['merkle_root'][:16]}...)")
            except Exception as e:
                logger.warning(f"Ledger finalization failed: {e}")
            
            # Step 4: Shutdown ThreadPoolExecutor
            logger.info("Step 4: Shutting down ThreadPoolExecutor...")
            self.arbiter.executor.shutdown(wait=True, cancel_futures=False)
            logger.info("✓ Executor shutdown complete")
            
            # Final status
            logger.info("=" * 60)
            logger.info("SHUTDOWN COMPLETE")
            logger.info(f"  Total beats executed: {self.arbiter.beat_count}")
            logger.info(f"  Ledger entries: {self.arbiter.ledger.get_chain_length()}")
            logger.info(f"  PID stable: {self.arbiter.pid.is_stable()}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        # Exit cleanly
        sys.exit(0)
