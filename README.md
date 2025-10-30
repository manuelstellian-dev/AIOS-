# VENOM Λ-GENESIS - Fractal Organism Architecture

**Autonomous AI Operating System** - A fractal organism orchestrated by Arbiter with 4 parallel flows (R, B, E, O) synchronized via T_Λ pulse, genomic PID stability control, and immutable SHA3 ledger.

## Architecture Overview

VENOM Λ-GENESIS is a **fractal organism** with Lyapunov stability (ΔV < 0) and continuous recalibration, designed to be coherent, integrated, and 100% functional.

### Core Components

1. **Arbiter** - The Decisional Brain
   - Parallel orchestration using `ThreadPoolExecutor` with 4 workers
   - Aggregates recommendations from cores with weighted decision vector
   - Threshold-based decision making (QUARANTINE, ALERT, BALANCE, OPTIMIZE)
   - PID recalibration to maintain stability

2. **T_Λ Pulse** - Time Compression Synchronization
   - Formula: `T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP))` for kP > 1
   - Parameters: k=4 (flows), P=5 (nodes), T1=0.001s, U=exp(4)≈54.6
   - Ensures Perfectly Well-Posed Stability (WPS)

3. **Genomic PID Controller**
   - Maintains Lyapunov stability (ΔV < 0)
   - Error: ΔT = T_Λ - T_threshold (T_threshold = 0.02)
   - Anti-windup: integral clamped to [-1.0, 1.0]
   - ε-reset: integral reset when |ΔT| < 1e-4
   - Weight adjustment: ΔO limited to ±0.05 per beat

4. **Four Parallel Cores**
   - **RegenCore (R)**: Repair/replication planning (urgency, cost)
   - **BalanceCore (B)**: Stabilization, PID parameters (Kp=0.6, Ki=0.1, Kd=0.05)
   - **EntropyCore (E)**: Risk scanning, threat inference
   - **OptimizeCore (O)**: Reinvestment, transformation (expected_gain)

5. **Entropy Model** - Torch Neural Network
   - Architecture: `torch.nn.Linear(1, 1)` with Sigmoid
   - Input: total_anoms (anomalies from features + genome)
   - Output: threat_score bounded in [0, 1]
   - ML weight: 0.12 (default, updatable)

6. **Immutable Ledger** - SHA3-256 Blockchain
   - Append-only log with canonical JSON (sorted keys, no whitespace)
   - Merkle root for integrity verification
   - Records pulses, flow results, and actions

7. **P2P Mesh** - Nanobot Phalanx
   - FIFO Queue-based message delivery
   - Adaptive delay: 0.3ms if queue > 100, else 1ms
   - Broadcast to all nanobots except sender
   - Direct anomaly/ml_weight injection into genome

## Installation

```bash
# Clone repository
git clone https://github.com/manuelstellian-dev/AIOS-.git
cd AIOS-

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Quick Start

### Run Example

```bash
python example.py
```

### Run Main Application

```bash
# Run for 10 beats
python main.py --beats 10

# Run infinite beats
python main.py --beats -1

# With P2P mesh
python main.py --beats -1 --mesh --mesh-port 9000

# Custom parameters
python main.py --beats 100 --k-flows 4 --p-nodes 5 --t1 0.001 --t-threshold 0.02
```

## Usage

```python
from venom import (
    Arbiter,
    TLambdaPulse,
    GenomicPID,
    EntropyModel,
    ImmutableLedger,
    P2PMesh
)

# Initialize components
pulse = TLambdaPulse(k=4, p=5, t1=0.001)
pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
entropy_model = EntropyModel(ml_weight=0.12)
ledger = ImmutableLedger()
mesh = P2PMesh(node_id="venom-node-1", port=9000)

# Create Arbiter
arbiter = Arbiter(
    pulse=pulse,
    pid=pid,
    entropy_model=entropy_model,
    ledger=ledger,
    mesh=mesh
)

# Start execution
arbiter.start(beats=10)

# Get status
status = arbiter.get_status()
print(f"Beats executed: {status['beat']}")
print(f"PID stable: {status['pid_stable']}")
print(f"Ledger verified: {status['ledger_verified']}")

# Get ledger manifest
manifest = ledger.get_manifest()
print(f"Merkle Root: {manifest['merkle_root']}")
```

## Kubernetes Deployment

### Deploy to K8s

```bash
# Apply deployment (includes HPA with CPU 50% threshold)
kubectl apply -f k8s/deployment.yaml

# Apply service (LoadBalancer on port 8000)
kubectl apply -f k8s/svc.yaml

# Check status
kubectl get pods -l app=venom
kubectl get svc venom-genesis
kubectl get hpa venom-genesis-hpa

# Scale manually
kubectl scale deployment venom-genesis --replicas=5

# View logs
kubectl logs -f deployment/venom-genesis
```

### HPA Configuration

The HorizontalPodAutoscaler scales replicas from 1 to 10 based on CPU utilization:
- Target: 50% CPU utilization
- Min replicas: 1
- Max replicas: 10
- Scale up: aggressive (100% increase per 30s)
- Scale down: conservative (50% decrease per 60s with 5min stabilization)

## Docker

### Build Image

```bash
docker build -t venom:latest .
```

### Run Container

```bash
# Run with default config
docker run -p 8000:8000 venom:latest

# Run with custom parameters
docker run -p 8000:8000 venom:latest python main.py --beats 100

# Interactive mode
docker run -it venom:latest /bin/bash
```

## Architecture Details

### Decision Thresholds

```python
THREAT_QUARANTINE = 0.85  # Quarantine if threat >= 0.85
THREAT_ALERT = 0.60       # Alert if threat >= 0.60
STABILITY_THRESHOLD = 0.25  # Balance threshold
REPAIR_THRESHOLD = 0.1    # Repair threshold
OPT_GAIN_THRESHOLD = 0.1  # Optimize threshold
```

### Genome Evolution

Weights are continuously adjusted:
- **O weight**: Adjusted by PID output (ΔO limited to ±0.05)
- **E weight**: Hybrid feedback formula when threat > 0.5:
  ```
  E = 0.15 * threat * e^(-t/50) * (1 - O/0.3)
  ```
- **Normalization**: All weights normalized to sum to 1.0

### Time Compression

The T_Λ pulse ensures stability with:
```
T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP))
```

Where:
- T1 = 0.001 (base time)
- k = 4 (parallel flows)
- P = 5 (initial nodes)  
- U = exp(4) ≈ 54.6
- Minimum bound: 1e-6 for numerical stability

### PID Control

```
Error: ΔT = T_Λ - T_threshold
Output: PID_out = Kp*ΔT + Ki*∫ΔT*dt + Kd*d(ΔT)/dt

Anti-windup: ∫ΔT*dt ∈ [-1.0, 1.0]
ε-reset: if |ΔT| < 1e-4 then ∫ΔT*dt = 0
```

## Project Structure

```
AIOS-/
├── venom/                  # Main package
│   ├── core/              # Core components
│   │   ├── arbiter.py     # Arbiter orchestrator
│   │   └── constants.py   # System constants
│   ├── flows/             # Parallel cores
│   │   └── parallel_flows.py  # R, B, E, O cores
│   ├── sync/              # Synchronization
│   │   └── pulse.py       # T_Λ pulse generator
│   ├── control/           # Control systems
│   │   └── genomic_pid.py # PID controller
│   ├── inference/         # AI models
│   │   └── entropy_model.py  # Torch entropy model
│   ├── ledger/            # Blockchain
│   │   └── immutable_ledger.py  # SHA3 ledger
│   └── mesh/              # Networking
│       └── p2p.py         # P2P mesh
├── k8s/                   # Kubernetes configs
│   ├── deployment.yaml    # Deployment + HPA + ConfigMap
│   └── svc.yaml          # LoadBalancer service
├── main.py               # Main entry point
├── example.py            # Usage example
├── Dockerfile            # Container image
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Contributing

This is an autonomous AI operating system with fractal architecture. Contributions should maintain:
- Lyapunov stability (ΔV < 0)
- Parallel execution consistency
- Ledger immutability
- PID control precision

## License

See LICENSE file for details.

## References

- **Lyapunov Stability**: Ensures ΔV < 0 for system convergence
- **Fractal Architecture**: Self-similar patterns across scales
- **Time Compression**: T_Λ formula for perfectly well-posed stability
- **Genomic Evolution**: Continuous weight adaptation with normalization
- **Blockchain**: SHA3-256 immutable ledger with Merkle root 
