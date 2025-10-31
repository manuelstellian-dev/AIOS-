#!/usr/bin/env python3
"""
VENOM Λ-GENESIS Example Usage
Demonstrates the fractal organism architecture
"""
import logging

from venom import (
    Arbiter,
    TLambdaPulse,
    GenomicPID,
    EntropyModel,
    ImmutableLedger,
    Constants
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Example demonstrating VENOM Λ-GENESIS architecture"""
    
    print("=" * 70)
    print("VENOM Λ-GENESIS - Fractal Organism Architecture Example")
    print("=" * 70)
    print()
    
    # Component 1: T_Λ Pulse (Time Compression)
    print("1. T_Λ Pulse - Time Compression Synchronization")
    print(f"   Formula: T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP)) for kP > 1")
    print(f"   Parameters: k=4, P=5, T1=0.001, U=exp(4)≈54.6")
    
    pulse = TLambdaPulse(k=4, p=5, t1=0.001)
    t_lambda = pulse.compute_t_lambda()
    print(f"   Computed T_Λ: {t_lambda:.6f} seconds")
    print()
    
    # Component 2: Genomic PID Controller
    print("2. Genomic PID Controller - Stability (ΔV < 0)")
    print(f"   Parameters: Kp=0.6, Ki=0.1, Kd=0.05 (from BalanceCore)")
    print(f"   T_threshold: {Constants.T_THRESHOLD}")
    print(f"   Anti-windup: integral clamped to [-1.0, 1.0]")
    print(f"   ε-reset: integral reset when |ΔT| < {Constants.EPSILON_RESET}")
    
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    pid_result = pid.compute(t_lambda)
    print(f"   ΔT: {pid_result['delta_t']:.6f}")
    print(f"   ΔV: {pid_result['delta_v']:.6f}")
    print(f"   Stable: {pid_result['stable']}")
    print(f"   Weight adjustment: {pid_result['weight_adjustment']:.6f}")
    print()
    
    # Component 3: Entropy Model (Torch)
    print("3. Entropy Model - Torch Linear(1, 1) + Sigmoid")
    print(f"   Architecture: Input(1) -> Linear(1,1) -> Sigmoid -> Output(1)")
    print(f"   ML Weight: 0.12 (default)")
    
    entropy_model = EntropyModel(ml_weight=0.12)
    threat_score = entropy_model.infer_threat(total_anoms=5)
    print(f"   Threat score for 5 anomalies: {threat_score:.4f}")
    print()
    
    # Component 4: Immutable Ledger
    print("4. Immutable Ledger - SHA3-256 Blockchain")
    print(f"   Features: Append-only, canonical JSON, Merkle root")
    
    ledger = ImmutableLedger()
    entry = ledger.record_action("EXAMPLE", {"value": 42})
    print(f"   Genesis hash: {ledger.chain[0].hash[:16]}...")
    print(f"   New entry hash: {entry.hash[:16]}...")
    print(f"   Chain verified: {ledger.verify_chain()}")
    manifest = ledger.get_manifest()
    print(f"   Merkle root: {manifest['merkle_root'][:16]}...")
    print()
    
    # Component 5: Arbiter (Orchestrator)
    print("5. Arbiter - The Decisional Brain")
    print(f"   Orchestration: ThreadPoolExecutor with 4 workers")
    print(f"   Cores: RegenCore(R), BalanceCore(B), EntropyCore(E), OptimizeCore(O)")
    print(f"   Decision thresholds:")
    print(f"     QUARANTINE: threat >= {Constants.THREAT_QUARANTINE}")
    print(f"     ALERT: threat >= {Constants.THREAT_ALERT}")
    print(f"     APPLY_BALANCE: stability > {Constants.STABILITY_THRESHOLD}")
    print(f"     APPLY_OPTIMIZE: opt_gain > {Constants.OPT_GAIN_THRESHOLD}")
    print()
    
    arbiter = Arbiter(
        pulse=pulse,
        pid=pid,
        entropy_model=entropy_model,
        ledger=ledger
    )
    
    print("6. Executing 5 beats...")
    print()
    
    for beat in range(5):
        summary = arbiter.execute_beat()
        print(f"   Beat {summary['beat']}:")
        print(f"     Action: {summary['action']}")
        print(f"     T_Λ: {summary['t_lambda']:.6f}")
        print(f"     Threat: {summary['decvec']['raw_threat']:.4f}")
        print(f"     Weights: R={summary['weights']['R']:.3f}, "
              f"B={summary['weights']['B']:.3f}, "
              f"E={summary['weights']['E']:.3f}, "
              f"O={summary['weights']['O']:.3f}")
        print(f"     PID Stable: {summary['pid_stable']}")
        print()
    
    arbiter.stop()
    
    # Final summary
    print("=" * 70)
    print("Final System Status")
    print("=" * 70)
    status = arbiter.get_status()
    print(f"Total beats executed: {status['beat']}")
    print(f"PID stability: {status['pid_stable']}")
    print(f"Ledger entries: {status['ledger_length']}")
    print(f"Ledger integrity: {status['ledger_verified']}")
    print(f"Final genome weights: {status['genome']['weights']}")
    print()
    
    manifest = ledger.get_manifest()
    print("Ledger Manifest:")
    print(f"  Merkle Root: {manifest['merkle_root']}")
    print(f"  Chain Length: {manifest['chain_length']}")
    print()
    
    print("=" * 70)
    print("VENOM Λ-GENESIS architecture demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
