# VENOM Quick Start Guide

Get up and running with VENOM Framework in minutes!

## Prerequisites

Ensure VENOM is installed. If not, see [Installation Guide](installation.md).

```bash
venom --version
# VENOM v1.0.0
```

## Your First VENOM Program

### 1. Basic Arbiter Setup

Create `my_first_venom.py`:

```python
from venom.core import Arbiter, TLambdaPulse, GenomicPID
from venom.inference import EntropyModel
from venom.ledger import ImmutableLedger

# Initialize components
pulse = TLambdaPulse(k=4, p=5, t1=0.001)
pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05)
entropy = EntropyModel(ml_weight=0.12)
ledger = ImmutableLedger()

# Create arbiter
arbiter = Arbiter(
    pulse=pulse,
    pid=pid,
    entropy_model=entropy,
    ledger=ledger
)

# Run for 10 beats
print("Starting VENOM Arbiter...")
arbiter.start(beats=10)
print("Completed!")
```

Run it:
```bash
python my_first_venom.py
```

### 2. Using the CLI

```bash
# Check system health
venom health check

# Scan hardware
venom-omega scan

# List available modules
venom modules list

# Get module info
venom modules info ml
```

## Common Use Cases

### AI Model Training

```python
from venom.ml import AutoMLPipeline

# Initialize AutoML
pipeline = AutoMLPipeline(framework='optuna')

# Define objective function
def objective(trial):
    lr = trial.suggest_float('lr', 0.001, 0.1)
    layers = trial.suggest_int('layers', 2, 10)
    
    # Your model training code here
    # Return metric to optimize (e.g., accuracy)
    return accuracy

# Run hyperparameter tuning
best_params = pipeline.tune_hyperparameters(
    objective_fn=objective,
    search_space={
        'lr': (0.001, 0.1),
        'layers': (2, 10)
    },
    n_trials=50,
    direction='maximize'
)

print(f"Best parameters: {best_params}")
```

### Document Management

```python
from venom.knowledge import DocumentStore, SemanticSearch

# Initialize document store
store = DocumentStore()

# Add documents
doc_id1 = store.add_document(
    "VENOM is a universal AI operating system",
    {"category": "intro", "version": "1.0"}
)

doc_id2 = store.add_document(
    "The framework includes ML, security, and cloud features",
    {"category": "features", "version": "1.0"}
)

# Search documents
search = SemanticSearch()
results = search.search("AI features", top_k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content']}")
```

### Security & Encryption

```python
from venom.security import AdvancedEncryption

# Initialize encryption
encryption = AdvancedEncryption(algorithm='aes-gcm')

# Generate key
key = encryption.generate_key()

# Encrypt data
plaintext = b"Sensitive information"
encrypted, nonce = encryption.encrypt(plaintext, key)

print(f"Encrypted: {encrypted[:20]}...")

# Decrypt data
decrypted = encryption.decrypt(encrypted, key, nonce)
assert decrypted == plaintext
print("Encryption/Decryption successful!")
```

### Cloud Deployment

```python
from venom.cloud.aws import EKSDeployer

# Initialize deployer
deployer = EKSDeployer(
    cluster_name="venom-prod",
    region="us-east-1"
)

# Get cluster info
config = deployer.get_deployment_config()
print(f"Cluster: {config['cluster_name']}")
print(f"Region: {config['region']}")

# Deploy (requires actual cluster)
# deployer.deploy(manifest_path="./k8s/deployment.yaml")
```

### Monitoring & Observability

```python
from venom.observability import ThetaMonitor
import time

# Initialize monitor
monitor = ThetaMonitor(interval=1.0)

# Start monitoring
monitor.start_monitoring()
print("Monitoring system health...")

# Let it collect metrics
time.sleep(5)

# Get current status
status = monitor.get_current_status()
print(f"System Theta: {status['theta']:.3f}")
print(f"CPU Health: {status['cpu_health']:.3f}")
print(f"Memory Health: {status['memory_health']:.3f}")

# Stop monitoring
monitor.stop_monitoring()
```

## CLI Workflows

### Complete AI Workflow

```bash
# 1. Check system
venom health check

# 2. Train model
venom ai train --model transformer --data ./data/train.csv

# 3. Run predictions
venom ai predict --model ./models/transformer_model.pt --input "test data"
```

### Security Workflow

```bash
# 1. Encrypt sensitive files
venom security encrypt --file ./secrets/api_keys.txt

# 2. Scan codebase for security issues
venom security scan --path ./src

# 3. Verify encryption
ls -la ./secrets/
```

### Cloud Deployment Workflow

```bash
# 1. Check cloud status
venom cloud status

# 2. Deploy to AWS
venom cloud deploy --provider aws --config ./deploy/aws.json

# 3. Monitor deployment
venom health metrics
```

### Knowledge Management Workflow

```bash
# 1. Add documents
venom knowledge add --doc ./docs/guide.md --metadata '{"type":"guide"}'
venom knowledge add --doc ./docs/api.md --metadata '{"type":"api"}'

# 2. Search
venom knowledge search --query "deployment guide"

# 3. Verify storage
ls -la .venom/knowledge/
```

## Omega CLI (Temporal Compression)

### Hardware Profiling

```bash
# Scan your hardware
venom-omega scan

# View configuration
venom-omega config
```

### Performance Estimation

```bash
# Calculate compression for 840h workload
venom-omega compress 840

# Output:
# 🌌 Temporal Compression Estimate
# Sequential Time: 840.0 hours
# Parallel Time:   17.5 hours
# Total Speedup:   48.0x
```

### Benchmarking

```bash
# Run performance benchmark
venom-omega benchmark

# Monitor real-time
venom-omega monitor --duration 30
```

## Working with Configuration

### Create Configuration File

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
  },
  "knowledge": {
    "storage_path": "~/.venom/knowledge",
    "embedding_model": "sentence-transformers"
  }
}
```

### Load Configuration in Code

```python
import json
from pathlib import Path

config_file = Path.home() / ".venomrc"
if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
    
    log_level = config.get('log_level', 'INFO')
    metrics_port = config.get('metrics_port', 8000)
```

## Docker Quick Start

### Single Container

```bash
# Build
docker build -t venom:1.0.0 .

# Run
docker run -p 8000:8000 venom:1.0.0

# Access metrics
curl http://localhost:8000/metrics
```

### Full Stack with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# Access services
# - VENOM metrics: http://localhost:8000/metrics
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/venom)

# Stop services
docker-compose down
```

## Testing Your Setup

### Run Tests

```bash
# All tests
pytest

# Integration tests
pytest tests/integration/

# Performance benchmarks
pytest tests/performance/

# With coverage
pytest --cov=venom --cov-report=html
```

### Manual Testing

```python
# Create test script: test_setup.py
from venom.core import Arbiter, TLambdaPulse, GenomicPID
from venom.inference import EntropyModel
from venom.ledger import ImmutableLedger

def test_basic_setup():
    """Test basic VENOM setup"""
    pulse = TLambdaPulse(k=4, p=5, t1=0.001)
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05)
    entropy = EntropyModel(ml_weight=0.12)
    ledger = ImmutableLedger()
    
    arbiter = Arbiter(
        pulse=pulse,
        pid=pid,
        entropy_model=entropy,
        ledger=ledger
    )
    
    print("✓ All components initialized")
    print("✓ VENOM setup successful")

if __name__ == '__main__':
    test_basic_setup()
```

Run it:
```bash
python test_setup.py
```

## Next Steps

Now that you're up and running:

1. **Explore Modules**: Check out [Module Documentation](modules/)
2. **Read Architecture**: Understand the [Architecture](../ARCHITECTURE.md)
3. **Try Examples**: Browse [Code Examples](examples/)
4. **CLI Reference**: Master the [CLI](cli.md)
5. **Advanced Topics**: Learn about [Möbius Engine](MOBIUS_ENGINE.md)

## Getting Help

- **Documentation**: Browse [all docs](.)
- **Examples**: See [examples/](examples/)
- **Issues**: Report [GitHub Issues](https://github.com/manuelstellian-dev/AIOS-/issues)
- **Community**: Join [Discussions](https://github.com/manuelstellian-dev/AIOS-/discussions)

---

**You're ready to build with VENOM! 🚀**
