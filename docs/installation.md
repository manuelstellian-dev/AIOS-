# VENOM Installation Guide

This guide covers installation of the VENOM Framework on various platforms.

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version recommended
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM
- **Disk Space**: 2GB free space

## Standard Installation

### 1. Clone the Repository

```bash
git clone https://github.com/manuelstellian-dev/AIOS-.git
cd AIOS-
```

### 2. Create Virtual Environment (Recommended)

```bash
# Linux/macOS
python3 -m venv venv
source venom/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install VENOM

```bash
# Development installation (editable)
pip install -e .

# Or standard installation
pip install .
```

### 5. Verify Installation

```bash
# Check version
venom --version

# Run health check
venom health check

# Test CLI
venom modules list
```

## Platform-Specific Instructions

### Linux

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Install VENOM
pip install -e .
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Install VENOM
pip3 install -e .
```

### Windows

```powershell
# Install Python from python.org or Microsoft Store

# Install Visual C++ Build Tools (if needed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install VENOM
pip install -e .
```

## Optional Components

### Cloud Provider SDKs

#### AWS
```bash
pip install boto3 kubernetes
```

#### Google Cloud
```bash
pip install google-cloud-container google-cloud-storage google-cloud-functions
```

#### Azure
```bash
pip install azure-mgmt-containerservice azure-storage-blob azure-functions azure-identity
```

### Analytics & ML
```bash
pip install scipy scikit-learn xgboost
```

### Database Connectors
```bash
pip install psycopg2-binary mysql-connector-python
```

## Hardware-Specific Setup

### NVIDIA CUDA

For CUDA GPU support:

```bash
# Install CUDA Toolkit from NVIDIA
# https://developer.nvidia.com/cuda-downloads

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### AMD ROCm

For AMD GPU support:

```bash
# Install ROCm
# https://docs.amd.com/

pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.6
```

### Apple Silicon (M1/M2/M3)

```bash
# Use native ARM Python
pip install torch torchvision
```

### Raspberry Pi

```bash
# Install system dependencies
sudo apt-get install python3-dev libatlas-base-dev

# Install VENOM
pip3 install -e .

# Note: Some heavy ML features may be limited
```

## Docker Installation

### Using Docker

```bash
# Build image
docker build -t venom:1.0.0 .

# Run container
docker run -p 8000:8000 venom:1.0.0
```

### Using Docker Compose

```bash
# Start full stack (VENOM + Prometheus + Grafana)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f venom
```

## Kubernetes Installation

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/svc.yaml

# Verify deployment
kubectl get pods -l app=venom
kubectl get svc venom-service

# Check auto-scaling
kubectl get hpa venom-genesis-hpa
```

## Configuration

### Configuration File

Create `~/.venomrc`:

```json
{
  "log_level": "INFO",
  "metrics_port": 8000,
  "enable_prometheus": true,
  "cloud": {
    "default_provider": "aws",
    "aws_region": "us-east-1"
  },
  "security": {
    "enable_encryption": true,
    "enable_signing": true
  }
}
```

### Environment Variables

```bash
export VENOM_LOG_LEVEL=INFO
export VENOM_METRICS_PORT=8000
export VENOM_CLOUD_PROVIDER=aws
export VENOM_AWS_REGION=us-east-1
```

## Verification

### Run Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_integration.py

# Run with coverage
pytest --cov=venom
```

### Check Health

```bash
# CLI health check
venom health check

# System scan
venom-omega scan

# View metrics
venom health metrics
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'venom'

Solution:
```bash
pip install -e .
```

#### CUDA not found

Solution:
```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

#### Permission denied

Solution:
```bash
# Linux/macOS
sudo chown -R $USER:$USER ~/.venom

# Windows: Run as administrator
```

### Getting Help

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/manuelstellian-dev/AIOS-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manuelstellian-dev/AIOS-/discussions)

## Next Steps

- Read the [Quick Start Guide](quickstart.md)
- Explore [CLI Reference](cli.md)
- Check out [Examples](examples/)
- Review [Architecture](../ARCHITECTURE.md)

---

**Installation complete! Ready to use VENOM Framework.**
