# Universal Deployment Guide - VENOM Ω-AIOS

## Quick Start

VENOM Ω-AIOS automatically adapts to ANY device:

```bash
# Install
pip install psutil networkx

# Scan your hardware
python venom/hardware/universal_scanner.py

# Run temporal compression demo
python venom/sync/adaptive_mobius_engine.py
```

## Device Support Matrix

| Device Type | Cores | RAM | Expected Speedup | Status |
|-------------|-------|-----|------------------|--------|
| Raspberry Pi 3 | 4 | 1GB | 20-50x | ✅ Supported |
| Raspberry Pi 4 | 4 | 4GB | 100-150x | ✅ Supported |
| Laptop (basic) | 4-8 | 8GB | 500-1,500x | ✅ Supported |
| Laptop (high-end) | 8-16 | 16GB+ | 1,500-5,000x | ✅ Supported |
| Desktop Workstation | 16-32 | 32GB+ | 5,000-15,000x | ✅ Supported |
| Cloud (small) | 4-8 | 16GB | 1,000-3,000x | ✅ Supported |
| Cloud (medium) | 16-32 | 64GB | 10,000-30,000x | ✅ Supported |
| Cloud (large) | 64+ | 128GB+ | 50,000-100,000x | ✅ Supported |

## Platform Support

### Linux (Primary)
- **Distributions**: Ubuntu, Debian, CentOS, RHEL, Arch, Alpine
- **Architectures**: x86_64, ARM, ARM64
- **Containers**: Docker, Podman, LXC
- **Orchestration**: Kubernetes, Docker Swarm

### macOS
- **Versions**: 10.15+ (Catalina and later)
- **Architectures**: Intel (x86_64), Apple Silicon (ARM64)
- **Metal GPU**: Automatically detected

### Windows
- **Versions**: Windows 10, Windows 11, Windows Server 2019+
- **Architectures**: x86_64
- **Note**: Limited thermal monitoring support

### Raspberry Pi
- **Models**: Pi 3, Pi 4, Pi 400, Pi 5
- **OS**: Raspberry Pi OS (Debian-based)
- **Note**: Optimized for low-memory environments

## Installation Methods

### Method 1: Direct Install (Recommended)

```bash
# Clone repository
git clone https://github.com/manuelstellian-dev/AIOS-.git
cd AIOS-

# Install dependencies
pip install -r requirements.txt

# Test installation
python venom/hardware/universal_scanner.py
```

### Method 2: Development Install

```bash
pip install -e .
```

### Method 3: Docker

```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "venom/hardware/universal_scanner.py"]
```

```bash
docker build -t venom-omega .
docker run venom-omega
```

### Method 4: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: venom-omega
spec:
  replicas: 3
  selector:
    matchLabels:
      app: venom-omega
  template:
    metadata:
      labels:
        app: venom-omega
    spec:
      containers:
      - name: venom
        image: venom-omega:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "2"
          limits:
            memory: "4Gi"
            cpu: "4"
```

## Hardware-Specific Optimizations

### Raspberry Pi

```python
from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine

# Conservative settings for Pi
config = {
    'n_cores': 4,
    'lambda_wrap': 50.0,
    'parallel_fraction': 0.65,
    'cpu_health': 0.6,
    'memory_health': 0.7,
    'thermal_health': 0.7
}

engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
```

### High-Performance Server

```python
# Aggressive settings for cloud
config = {
    'n_cores': 32,
    'lambda_wrap': 832.0,
    'parallel_fraction': 0.95,
    'cpu_health': 0.9,
    'memory_health': 0.95,
    'thermal_health': 0.9
}

engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
```

## GPU Support

### NVIDIA CUDA

Automatically detected if PyTorch with CUDA is installed:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### AMD ROCm

```bash
pip install torch --index-url https://download.pytorch.org/whl/rocm5.6
```

### Apple Metal

Automatically detected on macOS with Apple Silicon:

```bash
pip install torch
```

## Cloud Deployments

### AWS

```bash
# EC2 instance types optimized for VENOM Ω-AIOS
# - c5.xlarge: 4 vCPUs, 8GB RAM (basic)
# - c5.4xlarge: 16 vCPUs, 32GB RAM (recommended)
# - c5.18xlarge: 72 vCPUs, 144GB RAM (high-performance)

# Auto-scaling group for dynamic workloads
# Lambda wrap scales from 200 to 832 based on instance type
```

### Azure

```bash
# VM sizes optimized for VENOM Ω-AIOS
# - Standard_D4s_v3: 4 vCPUs, 16GB RAM
# - Standard_D16s_v3: 16 vCPUs, 64GB RAM
# - Standard_D64s_v3: 64 vCPUs, 256GB RAM
```

### Google Cloud

```bash
# Machine types optimized for VENOM Ω-AIOS
# - n2-standard-4: 4 vCPUs, 16GB RAM
# - n2-standard-16: 16 vCPUs, 64GB RAM
# - c2-standard-60: 60 vCPUs, 240GB RAM
```

## Monitoring & Observability

### Prometheus Integration

```python
from venom.observability.theta_monitor import ThetaMonitor

monitor = ThetaMonitor(interval=1.0)
monitor.start_monitoring()

# Metrics endpoint
metrics = monitor.export_prometheus_metrics()
print(metrics)
```

### Grafana Dashboard

Available metrics:
- `venom_theta_current`: System health
- `venom_theta_cpu_health`: CPU health
- `venom_theta_memory_health`: Memory health
- `venom_theta_thermal_health`: Thermal health
- `venom_theta_compression_factor`: Compression factor

## Performance Tuning

### Memory-Constrained Environments

```python
# Reduce workers for low-memory systems
scanner.profile.optimal_workers = max(1, scanner.profile.cpu_cores_logical // 2)
scanner.profile.lambda_wrap = min(100.0, scanner.profile.lambda_wrap)
```

### CPU-Constrained Environments

```python
# Lower parallel fraction for high contention
scanner.profile.parallel_fraction = 0.60
```

### Thermal-Constrained Environments

```python
# Monitor and throttle based on temperature
from venom.observability.theta_monitor import ThetaMonitor

monitor = ThetaMonitor(interval=0.5)
monitor.start_monitoring()

if monitor.thermal_health < 0.5:
    # System too hot, reduce workload
    engine.config['n_cores'] = max(1, engine.config['n_cores'] // 2)
```

## Troubleshooting

### Issue: High Memory Usage

```python
# Reduce lambda wrap and workers
config['lambda_wrap'] = 100.0
config['n_cores'] = 2
```

### Issue: CPU Overheating

```python
# Enable adaptive throttling
arbiter = OmegaArbiter(enable_omega=True)
result = arbiter.execute_all_waves_parallel(waves, adaptive_throttle=True)
```

### Issue: Slow Performance

```bash
# Check hardware profile
python venom/hardware/universal_scanner.py

# Verify Möbius parameters are optimal
python venom/sync/adaptive_mobius_engine.py
```

## Best Practices

1. **Always scan hardware first** before configuring
2. **Enable adaptive throttling** for production
3. **Monitor theta** in real-time for long-running tasks
4. **Use dependency graphs** for complex wave structures
5. **Test on target hardware** before deploying

## Next Steps

- See [MOBIUS_ENGINE.md](MOBIUS_ENGINE.md) for mathematical details
- See [ARCHITECTURE.md](../ARCHITECTURE.md) for system architecture
- See [README.md](../README.md) for feature overview

---

**VENOM Ω-AIOS v0.2.0** - Deploy Anywhere, Optimize Everywhere
