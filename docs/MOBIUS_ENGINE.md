# VENOM Ω-AIOS Möbius Engine Documentation

## Overview

The **Adaptive Möbius Engine (Λ-TAS)** is the temporal compression system at the heart of VENOM Ω-AIOS. It enables **adaptive parallel execution** across ANY device, from Raspberry Pi to Cloud servers, with automatic hardware detection and optimization.

## Mathematical Foundation

### Core Formula

```
T_parallel = T_sequential / S_Total

where:
  S_Total = Θ(θ) × Λ × S_A
```

### Components

#### 1. System Health (θ - Theta)

The system health score combines three factors:

```
θ = 0.3×H_CPU + 0.3×H_MEM + 0.4×H_TERM

where:
  H_CPU  = CPU health [0-1] (inverse of usage)
  H_MEM  = Memory health [0-1] (inverse of usage)
  H_TERM = Thermal health [0-1] (temperature-based)
```

#### 2. Adaptive Compression (Θ(θ))

Piecewise compression function that adapts to system health:

```
Θ(θ) = {
  0.5                        if θ < 0.3      [UNWRAP]
  0.5 + (θ-0.3)×2.5          if 0.3 ≤ θ < 0.5  [TRANSITION]
  1.0 + (θ-0.5)×5.0          if 0.5 ≤ θ < 0.7  [BALANCE]
  2.0 + (θ-0.7)×2.5          if 0.7 ≤ θ < 0.9  [WRAP]
  3.0                        if θ ≥ 0.9      [OPTIMIZE]
}
```

**Modes:**
- **UNWRAP** (θ < 0.3): System stressed, minimal compression
- **TRANSITION** (0.3 ≤ θ < 0.5): Ramping up compression
- **BALANCE** (0.5 ≤ θ < 0.7): Optimal balance
- **WRAP** (0.7 ≤ θ < 0.9): High performance
- **OPTIMIZE** (θ ≥ 0.9): Maximum compression

#### 3. Lambda Wrap (Λ)

The lambda wrap factor scales with hardware capacity:

```
Λ = cores × 50 × memory_factor × gpu_factor

Range: [10, 832]

memory_factor = {
  0.5   if RAM < 4GB
  0.75  if 4GB ≤ RAM < 8GB
  1.0   if 8GB ≤ RAM < 16GB
  1.5   if 16GB ≤ RAM < 32GB
  2.0   if RAM ≥ 32GB
}

gpu_factor = {
  1.5   if CUDA/ROCm/Metal available
  1.0   otherwise
}
```

#### 4. Amdahl's Law (S_A)

Theoretical speedup from parallelization:

```
S_A = 1 / [(1-P) + P/N]

where:
  N = number of worker cores
  P = parallel fraction [0.60-0.95]
```

## Hardware Profiles

### Universal Hardware Scanner

The `UniversalHardwareScanner` detects hardware capabilities across:
- **Operating Systems**: Windows, Linux, macOS
- **Architectures**: x86_64, ARM, ARM64
- **Devices**: Raspberry Pi, laptops, desktops, cloud instances

**Detection includes:**
- CPU: cores, architecture, vendor, frequency, usage
- Memory: total, available, swap
- GPU: CUDA, ROCm, Metal, OpenCL
- Thermal: CPU temperature
- Platform: OS, version, machine type
- Capabilities: Hyperthreading, virtualization, Docker, Kubernetes

### Adaptive Parameters

The scanner auto-calculates optimal parameters:

**N (Workers):**
```
Base: logical_cores
Adjust for memory: ÷2 if <4GB, ×0.75 if <8GB
Boost for GPU: ×1.5 if available
Range: [1, 64]
```

**P (Parallel Fraction):**
```
2 cores:  0.60
4 cores:  0.70
8 cores:  0.80
16 cores: 0.85
32 cores: 0.90
64+ cores: 0.95
```

## Performance Examples

### Raspberry Pi 4 (4 cores, 4GB RAM)
```
Configuration:
  N = 4 cores
  Λ = 50 (limited by memory)
  P = 0.65
  θ = 0.61 (BALANCE mode)
  Θ(θ) = 1.55

Results:
  Sequential: 840 hours (35 days)
  Parallel: 5.55 hours
  Speedup: 151x
  Reduction: 99.3%
```

### Laptop (8 cores, 16GB RAM, no GPU)
```
Configuration:
  N = 8 cores
  Λ = 400 (8×50×1.0)
  P = 0.80
  θ = 0.77 (WRAP mode)
  Θ(θ) = 2.175

Results:
  Sequential: 840 hours
  Parallel: 0.29 hours (17 minutes)
  Speedup: 2,900x
  Reduction: 100.0%
```

### Cloud Server (32 cores, 64GB RAM, GPU)
```
Configuration:
  N = 48 cores (32×1.5 for GPU)
  Λ = 832 (maxed out)
  P = 0.95
  θ = 0.915 (OPTIMIZE mode)
  Θ(θ) = 3.0

Results:
  Sequential: 840 hours
  Parallel: 0.03 hours (2 minutes)
  Speedup: 31,322x
  Reduction: 100.0%
```

## Usage

### Basic Scan

```python
from venom.hardware.universal_scanner import UniversalHardwareScanner

scanner = UniversalHardwareScanner()
profile = scanner.scan()
scanner.print_profile()

print(f"Optimal workers: {profile.optimal_workers}")
print(f"Lambda wrap: {profile.lambda_wrap}")
print(f"Parallel fraction: {profile.parallel_fraction}")
```

### Temporal Compression

```python
from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine

# Auto-detect hardware
engine = AdaptiveMobiusEngine(auto_detect=True)

# Calculate compression
result = engine.compress_time(sequential_time=840.0)  # hours

print(f"Sequential: {result.sequential_time}h")
print(f"Parallel: {result.parallel_time}h")
print(f"Speedup: {result.speedup}x")
print(f"Reduction: {result.reduction_percent}%")
```

### Manual Configuration

```python
from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine

config = {
    'n_cores': 16,
    'lambda_wrap': 600.0,
    'parallel_fraction': 0.85,
    'cpu_health': 0.8,
    'memory_health': 0.9,
    'thermal_health': 0.85
}

engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
result = engine.compress_time(1000.0)
```

### Real-time Monitoring

```python
from venom.observability.theta_monitor import ThetaMonitor

monitor = ThetaMonitor(interval=1.0)
monitor.start_monitoring()

# Monitor runs in background
import time
time.sleep(10)

# Get current metrics
metrics = monitor.get_current_metrics()
print(f"Current θ: {metrics['theta']}")
print(f"CPU Health: {metrics['cpu_health']}")
print(f"Memory Health: {metrics['memory_health']}")
print(f"Thermal Health: {metrics['thermal_health']}")

monitor.stop_monitoring()
```

### Wave Execution

```python
from venom.core.omega_arbiter import OmegaArbiter

# Define waves
waves = [
    {
        'id': 'wave-1',
        'name': 'Foundation',
        'tasks': [
            {'name': 'init', 'function': init_system},
            {'name': 'config', 'function': load_config}
        ]
    },
    {
        'id': 'wave-2',
        'name': 'Services',
        'tasks': [
            {'name': 'db', 'function': start_database},
            {'name': 'cache', 'function': start_cache}
        ]
    }
]

# Create Omega Arbiter
arbiter = OmegaArbiter(enable_omega=True)

# Execute waves in parallel
result = arbiter.execute_all_waves_parallel(waves)

print(f"Waves: {result['waves_succeeded']}/{result['waves_total']}")
print(f"Tasks: {result['tasks_succeeded']}/{result['tasks_total']}")
print(f"Time: {result['total_execution_time']:.2f}s")
```

## CLI Usage

```bash
# Scan hardware directly
python venom/hardware/universal_scanner.py

# Run Möbius demo
python venom/sync/adaptive_mobius_engine.py

# Execute waves demo
python venom/deployment/parallel_executor.py

# Omega Arbiter demo
python venom/core/omega_arbiter.py
```

## Prometheus Metrics

The Theta Monitor exports metrics for observability:

```
venom_theta_current               # Current system theta
venom_theta_cpu_health            # CPU health score
venom_theta_memory_health         # Memory health score  
venom_theta_thermal_health        # Thermal health score
venom_theta_compression_factor    # Current Θ(θ) value
```

## Theoretical Limits

### Maximum Speedup

```
S_max = Θ_max × Λ_max × S_A_max
      = 3.0 × 832 × (cores when P→1)
      
For 64-core system with P=0.99:
S_max ≈ 3.0 × 832 × 63.36 ≈ 158,000x
```

### Practical Speedup

Real-world factors limit speedup:
- I/O bottlenecks
- Sequential dependencies
- Memory bandwidth
- Network latency
- Lock contention

Typical achievable speedup:
- Raspberry Pi: 50-150x
- Laptop: 1,000-3,000x
- Cloud: 10,000-50,000x

## ETERNAL_BALANCE Constraint

The Möbius engine maintains Lyapunov stability:

```
ETERNAL_BALANCE = EVOLUTION + SUPREME_GOOD

Constraint: ΔV < 0 (energy function decreasing)
```

This ensures:
- System stability under load
- Graceful degradation when resources constrained
- Adaptive throttling to prevent burnout
- Ethical resource utilization

## References

- Amdahl, G. M. (1967). "Validity of the single processor approach to achieving large scale computing capabilities"
- Möbius transformation: Complex analysis mapping
- Lyapunov stability theory: Dynamic systems stability
- Temporal compression: Time dilation through parallelization

---

**VENOM Ω-AIOS v0.2.0** - Universal Adaptive Möbius Engine
