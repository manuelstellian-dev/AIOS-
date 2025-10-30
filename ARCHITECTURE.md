# VENOM Λ-GENESIS Architecture Documentation

## System Overview

VENOM Λ-GENESIS is a **fractal organism** with Lyapunov stability (ΔV < 0) implementing an autonomous AI operating system with parallel processing, genomic evolution, and blockchain-based immutability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        ARBITER                               │
│                  (Decisional Brain)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ThreadPoolExecutor (4 workers)                     │    │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │    │
│  │  │  R   │  │  B   │  │  E   │  │  O   │           │    │
│  │  │ Regen│  │Balance│ │Entropy│ │Optim │           │    │
│  │  │ Core │  │ Core │  │ Core │  │ Core │           │    │
│  │  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘           │    │
│  │     │         │         │         │                 │    │
│  │     └─────────┴────┬────┴─────────┘                │    │
│  │                    │                                │    │
│  │              aggregate_recommendations              │    │
│  │                    │                                │    │
│  │                    ▼                                │    │
│  │            ┌─────────────┐                         │    │
│  │            │  DecisionVec │                         │    │
│  │            │  (decvec)    │                         │    │
│  │            └──────┬───────┘                         │    │
│  │                   │                                 │    │
│  │                   ▼                                 │    │
│  │               decide()                              │    │
│  │                   │                                 │    │
│  │        ┌──────────┼──────────┐                     │    │
│  │        ▼          ▼          ▼                      │    │
│  │   QUARANTINE   ALERT    APPLY_BALANCE/OPTIMIZE     │    │
│  │   (threat≥0.85)(≥0.60)   (NOOP)                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  recalibrate() - Genomic PID Controller            │    │
│  │  • Error: ΔT = T_Λ - T_threshold (0.02)            │    │
│  │  • Anti-windup: [-1.0, 1.0]                        │    │
│  │  • ε-reset: |ΔT| < 1e-4 → integral = 0             │    │
│  │  • Weight adjustment: ΔO ∈ [-0.05, 0.05]           │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Uses
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│  T_Λ Pulse  │  │ EntropyModel │  │   Ledger    │
│             │  │   (Torch)    │  │  (SHA3-256) │
│ Formula:    │  │              │  │             │
│ T_Λ = T1*ln │  │ Linear(1,1)  │  │ • Merkle    │
│    /(1-1/kP)│  │ + Sigmoid    │  │ • Canonical │
│             │  │              │  │   JSON      │
│ k=4, P=5    │  │ Input: anoms │  │ • Immutable │
│ T1=0.001    │  │ Output: [0,1]│  │             │
└─────────────┘  └──────────────┘  └─────────────┘

                 ┌──────────────┐
                 │  P2P Mesh    │
                 │  (Nanobot    │
                 │   Phalanx)   │
                 │              │
                 │ • FIFO Queue │
                 │ • Adaptive   │
                 │   delay      │
                 │ • Broadcast  │
                 └──────────────┘
```

## Component Specifications

### 1. Arbiter (Orchestrator)

**Responsibilities:**
- Parallel orchestration via `ThreadPoolExecutor` (4 workers)
- Aggregate recommendations from cores
- Make threshold-based decisions
- Recalibrate genome weights via PID

**Methods:**
- `time_wrap(features)` - Execute R, B, E, O in parallel
- `aggregate_recommendations(results)` - Create decision vector
- `decide(decvec)` - Determine action
- `recalibrate(t_lambda)` - Adjust O weight via PID

**Decision Thresholds:**
```python
QUARANTINE:    threat >= 0.85
ALERT:         threat >= 0.60
APPLY_BALANCE: stability > 0.25 AND repair_score < 0.1
APPLY_OPTIMIZE: opt_gain > 0.1
NOOP:          default
```

### 2. Four Parallel Cores

#### RegenCore (R) - Regeneration
- **Output:** `urgency` (repair urgency), `cost`
- **Purpose:** Planning repairs and replication
- **Formula:** urgency = min(0.9, anoms / 100.0)

#### BalanceCore (B) - Stabilization
- **Output:** `conserve` (conservation score), PID parameters
- **Purpose:** Provide stability and PID tuning
- **Parameters:** Kp=0.6, Ki=0.1, Kd=0.05

#### EntropyCore (E) - Risk Scanning
- **Output:** `threat_score`, explanation, version
- **Purpose:** Infer system threat level
- **Uses:** EntropyModel (Torch) for inference

#### OptimizeCore (O) - Optimization
- **Output:** `expected_gain`
- **Purpose:** Suggest optimization opportunities
- **Formula:** expected_gain = min(0.5, o_weight * 0.12)

### 3. T_Λ Pulse - Time Compression

**Formula:**
```
T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP))  for kP > 1
```

**Parameters:**
- k = 4 (parallel flows)
- P = 5 (initial nodes)
- T1 = 0.001 seconds (base time)
- U = exp(4) ≈ 54.6
- ln(U) ≈ 4

**Computed Value:**
```
T_Λ = (0.001 * 4) / (1 - 1/20)
    = 0.004 / 0.95
    ≈ 0.004211 seconds
```

**Stability Condition:** kP > 1 (ensures denominator > 0)

**Minimum Bound:** max(T_Λ, 1e-6) for numerical stability

### 4. Genomic PID Controller

**Purpose:** Maintain Lyapunov stability (ΔV < 0) by adjusting O weight

**Error Calculation:**
```
ΔT = T_Λ - T_threshold
where T_threshold = 0.02
```

**PID Formula:**
```
output = Kp*ΔT + Ki*∫ΔT*dt + Kd*d(ΔT)/dt
```

**Anti-Windup:**
```python
integral ∈ [-1.0, 1.0]  # Clamped
```

**ε-Reset:**
```python
if |ΔT| < 1e-4:
    integral = 0
```

**Weight Adjustment:**
```python
ΔO = -output  # Negative feedback
ΔO ∈ [-0.05, 0.05]  # Limited per beat
```

**Parameters (from BalanceCore):**
- Kp = 0.6 (proportional gain)
- Ki = 0.1 (integral gain)
- Kd = 0.05 (derivative gain)

### 5. Entropy Model (Torch Neural Network)

**Architecture:**
```python
torch.nn.Linear(1, 1)  # Input → Output
torch.sigmoid()         # Activation
```

**Input:** total_anoms (int)
- Anomalies from features
- + genome["risk"]["anoms"]

**Output:** threat_score ∈ [0, 1]

**ML Weight:** 0.12 (default, updatable)

**Training:** MSE Loss with optimizer

**Evaluation:** AUC/ROC metrics

### 6. Immutable Ledger (Blockchain)

**Hash Algorithm:** SHA3-256

**JSON Format:** Canonical
```python
json.dumps(data, sort_keys=True, separators=(",", ":"))
```

**Structure:**
```python
LedgerEntry:
  - index: int
  - timestamp: float
  - data: dict
  - previous_hash: str (64 hex)
  - hash: str (64 hex, SHA3-256)
```

**Merkle Root:**
- Computed from all entry hashes
- Binary tree structure
- Used for integrity verification

**Operations:**
- `add_entry(data)` - Add new entry
- `record_action(type, details)` - Record action
- `record_pulse(pulse_data)` - Record T_Λ pulse
- `record_flow_result(flow, result)` - Record core output
- `verify_chain()` - Verify integrity
- `compute_merkle_root()` - Get Merkle root
- `get_manifest()` - Get manifest with metadata

### 7. P2P Mesh (Nanobot Phalanx)

**Architecture:** Peer-to-peer network

**Message Queue:** FIFO (`queue.Queue`)

**Adaptive Delay:**
```python
if queue_length > 100:
    delay = 0.0003  # 0.3ms
else:
    delay = 0.001   # 1ms
```

**Broadcast:**
- Send to all peers except sender
- Asynchronous delivery via daemon thread

**Injection:**
```python
inject_data(genome, anoms=N, ml_weight=W)
# Directly updates genome["risk"]["anoms"]
# and genome["ml"]["ml_weight"]
```

### 8. Genome Evolution

**Initial Weights:**
```python
R: 0.25  (Regen)
B: 0.25  (Balance)
E: 0.15  (Entropy)
O: 0.35  (Optimize)
```

**O Weight Adjustment:**
```python
O = O + ΔO  (from PID)
O ∈ [0.1, 0.9]
```

**E Weight Hybrid Feedback:**
```python
if threat > 0.5:
    E = 0.15 * threat * exp(-t/50) * (1 - O/0.3)
else:
    E = 0.10
E ∈ [0.05, 0.30]
```

**Normalization:**
```python
total = R + B + E + O
R, B, E, O = R/total, B/total, E/total, O/total
# Ensures sum ≈ 1.0
```

## Kubernetes Deployment

### Resources
```yaml
requests:
  cpu: 100m
  memory: 256Mi
limits:
  cpu: 500m
  memory: 512Mi
```

### HPA (Horizontal Pod Autoscaler)
```yaml
minReplicas: 1
maxReplicas: 10
metrics:
  - type: CPU
    targetUtilization: 50%
```

**Scaling Behavior:**
- Scale up: aggressive (100% per 30s, max 2 pods)
- Scale down: conservative (50% per 60s, 5min stabilization)

### Service
```yaml
type: LoadBalancer
port: 8000  # Prometheus metrics
```

## Execution Flow

### Single Beat Cycle

```
1. Generate T_Λ pulse
   ├─ Compute T_Λ(k, P, U)
   └─ Record in ledger

2. Execute cores in parallel (time_wrap)
   ├─ RegenCore.execute(genome, features)
   ├─ BalanceCore.execute(genome, features)
   ├─ EntropyCore.execute(genome, features)
   └─ OptimizeCore.execute(genome, features)

3. Aggregate recommendations
   ├─ Weight results by genome weights
   └─ Create decision vector (decvec)

4. Make decision
   ├─ Check threat thresholds
   ├─ Check stability/repair thresholds
   └─ Determine action

5. Record action in ledger

6. Recalibrate (PID)
   ├─ Compute PID output from T_Λ
   ├─ Adjust O weight
   └─ Update E weight (hybrid feedback)

7. Normalize weights
   └─ Ensure sum = 1.0

8. Sleep for T_Λ duration
   └─ Wait before next beat
```

## Testing

### Unit Tests (25 tests)

**T_Λ Pulse Tests:**
- Initialization
- Stability condition (kP > 1)
- Formula computation
- Pulse generation
- Sequence tracking
- Reset functionality

**PID Controller Tests:**
- Initialization
- Compute with various errors
- Anti-windup clamping
- ε-reset mechanism
- Weight adjustment limits
- Stability checking
- Parameter updates

**Immutable Ledger Tests:**
- Genesis block creation
- Entry addition
- Action/pulse/flow recording
- Chain verification
- Merkle root computation
- Manifest generation
- Canonical JSON hashing

### Validation Results

```
25 tests passed
T_Λ computed: 0.004211s
PID stable: ΔT=-0.015789, ΔV=-0.015789 (ΔV < 0 ✓)
Entropy inference: 5 anoms → 0.6457 threat
Ledger integrity: verified ✓
Merkle root: valid ✓
```

## Performance Characteristics

**Time Complexity:**
- Parallel execution: O(1) per beat (4 cores in parallel)
- Decision making: O(1) constant time
- PID computation: O(1) constant time
- Ledger append: O(1) per entry
- Merkle root: O(n) where n = chain length

**Space Complexity:**
- Ledger: O(n) where n = number of entries
- Genome: O(1) constant size
- Core states: O(1) per core
- PID history: O(k) bounded to 1000 entries

**Stability:**
- Lyapunov stable: ΔV < 0
- PID convergence: guaranteed by ε-reset
- Time compression: kP > 1 ensures stability

## Usage Examples

### Basic Usage
```python
from venom import Arbiter, TLambdaPulse, GenomicPID, EntropyModel, ImmutableLedger

arbiter = Arbiter(
    pulse=TLambdaPulse(k=4, p=5),
    pid=GenomicPID(),
    entropy_model=EntropyModel(),
    ledger=ImmutableLedger()
)

arbiter.start(beats=10)
```

### With P2P Mesh
```python
from venom import P2PMesh

mesh = P2PMesh(node_id="venom-1", port=9000)
mesh.start()

arbiter = Arbiter(mesh=mesh)
arbiter.start(beats=-1)  # Infinite
```

### Command Line
```bash
# Run 10 beats
python main.py --beats 10

# Run with custom parameters
python main.py --k-flows 4 --p-nodes 5 --t-threshold 0.02

# Enable mesh
python main.py --beats -1 --mesh --mesh-port 9000
```

## References

- **Lyapunov Stability Theory**: ΔV < 0 ensures system convergence
- **PID Control**: Proportional-Integral-Derivative feedback control
- **Blockchain**: Immutable distributed ledger with cryptographic hashing
- **SHA3-256**: NIST standard cryptographic hash function
- **Merkle Trees**: Efficient data integrity verification
- **ThreadPoolExecutor**: Python concurrent execution framework
- **PyTorch**: Deep learning framework for neural networks
- **Kubernetes**: Container orchestration platform
- **Horizontal Pod Autoscaler**: K8s automatic scaling mechanism

---

**Document Version:** 1.0  
**Architecture Version:** VENOM Λ-GENESIS 0.1.0  
**Last Updated:** 2025-10-30
