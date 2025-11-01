#!/usr/bin/env python3
"""
Basic VENOM Example
Demonstrates core functionality of the VENOM Framework
"""

from venom.core import Arbiter, TLambdaPulse, GenomicPID
from venom.inference import EntropyModel
from venom.ledger import ImmutableLedger


def main():
    """Main example function"""
    
    print("=" * 60)
    print("VENOM Framework - Basic Example")
    print("=" * 60)
    print()
    
    # Initialize components
    print("Initializing VENOM components...")
    
    # Time compression pulse
    pulse = TLambdaPulse(k=4, p=5, t1=0.001)
    print(f"  ✓ T_Λ Pulse initialized (k={pulse.k}, p={pulse.p})")
    
    # PID controller for stability
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05)
    print(f"  ✓ Genomic PID initialized (Kp={pid.kp}, Ki={pid.ki}, Kd={pid.kd})")
    
    # Entropy model for threat prediction
    entropy = EntropyModel(ml_weight=0.12)
    print(f"  ✓ Entropy Model initialized (weight={entropy.ml_weight})")
    
    # Immutable ledger for data integrity
    ledger = ImmutableLedger()
    print(f"  ✓ Immutable Ledger initialized")
    
    print()
    
    # Create arbiter
    print("Creating Arbiter...")
    arbiter = Arbiter(
        pulse=pulse,
        pid=pid,
        entropy_model=entropy,
        ledger=ledger
    )
    print("  ✓ Arbiter created")
    print()
    
    # Run system for 5 beats
    print("Running VENOM system for 5 beats...")
    print("-" * 60)
    arbiter.start(beats=5)
    print("-" * 60)
    print()
    
    # Show final stats
    print("Final Statistics:")
    print(f"  Total Beats: {arbiter.beat_count}")
    print(f"  Ledger Entries: {len(ledger.chain)}")
    print(f"  System Status: Stable")
    print()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
