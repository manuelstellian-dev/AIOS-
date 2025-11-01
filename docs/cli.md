# VENOM CLI Reference

Complete reference for the VENOM command-line interface.

## Overview

VENOM provides two CLI tools:

1. **`venom`**: Main CLI for all VENOM operations
2. **`venom-omega`**: Ω-AIOS CLI for hardware profiling and temporal compression

## Main CLI: `venom`

### Global Options

```bash
venom --version          # Show version
venom --help             # Show help
venom <command> --help   # Show command-specific help
```

---

## Commands

### Module Management

#### `venom modules list`

List all available VENOM modules.

```bash
venom modules list
```

**Output:**
```
VENOM Modules
══════════════════════════════════════════════════════════════════
  core                 - Core components (Arbiter, Pulse, PID, Cores)
  ml                   - Machine learning and AI capabilities
  hardware             - Hardware bridges (CUDA, TPU, ROCm, Metal, WMI)
  cloud                - Cloud providers (AWS, GCP, Azure)
  security             - Security features (encryption, signing, MFA)
  knowledge            - Knowledge graph and document storage
  observability        - Monitoring and metrics (Prometheus, Theta)
  integrations         - External integrations (Slack, webhooks, databases)
  analytics            - Stream and predictive analytics
  deployment           - Edge and multi-region deployment
  ops                  - Operations (backup, audit, shutdown)
  testing              - Testing utilities (chaos engineering, load testing)
══════════════════════════════════════════════════════════════════
```

#### `venom modules info <module_name>`

Get detailed information about a specific module.

```bash
venom modules info ml
venom modules info security
venom modules info cloud
```

**Example:**
```bash
venom modules info ml
```

**Output:**
```
Module: ml
══════════════════════════════════════════════════════════════════
Description: Machine Learning and AI capabilities

Components:
  • AutoML
  • ModelServing
  • ModelRegistry
  • TransformerBridge
  • VisionModels

Example:
  from venom.ml import AutoMLPipeline
══════════════════════════════════════════════════════════════════
```

---

### AI & Machine Learning

#### `venom ai train`

Train an AI model with specified configuration.

```bash
venom ai train --model <model_type> --data <data_path>
```

**Options:**
- `--model` (required): Model type to train
- `--data` (required): Path to training data

**Examples:**
```bash
# Train transformer model
venom ai train --model transformer --data ./data/training.csv

# Train vision model
venom ai train --model resnet50 --data ./data/images/

# Train custom model
venom ai train --model custom --data ./data/train.jsonl
```

#### `venom ai predict`

Run prediction with a trained model.

```bash
venom ai predict --model <model_path> --input <input_data>
```

**Options:**
- `--model` (required): Path to trained model file
- `--input` (required): Input data for prediction

**Examples:**
```bash
# Text prediction
venom ai predict --model ./models/transformer.pt --input "sample text"

# Image prediction
venom ai predict --model ./models/resnet.pt --input ./images/photo.jpg

# JSON input
venom ai predict --model ./models/custom.pt --input '{"feature1": 0.5, "feature2": 1.2}'
```

---

### Security

#### `venom security encrypt`

Encrypt a file using AES-256-GCM encryption.

```bash
venom security encrypt --file <file_path>
```

**Options:**
- `--file` (required): Path to file to encrypt

**Output:**
- Creates `<filename>.encrypted` (encrypted file)
- Creates `<filename>.key` (encryption key)

**Examples:**
```bash
# Encrypt configuration file
venom security encrypt --file ./config/database.json

# Encrypt secrets
venom security encrypt --file ./secrets/api_keys.txt

# Encrypt document
venom security encrypt --file ./documents/sensitive.pdf
```

**Important:** Keep the `.key` file secure and separate from the encrypted file!

#### `venom security scan`

Scan directory for security vulnerabilities.

```bash
venom security scan --path <directory_path>
```

**Options:**
- `--path` (required): Directory path to scan

**Examples:**
```bash
# Scan source code
venom security scan --path ./src

# Scan entire project
venom security scan --path .

# Scan specific module
venom security scan --path ./venom/security
```

---

### Cloud Operations

#### `venom cloud deploy`

Deploy application to cloud provider.

```bash
venom cloud deploy --provider <provider> --config <config_path>
```

**Options:**
- `--provider` (required): Cloud provider (`aws`, `gcp`, or `azure`)
- `--config` (required): Path to deployment configuration file

**Examples:**
```bash
# Deploy to AWS
venom cloud deploy --provider aws --config ./deploy/aws-config.json

# Deploy to GCP
venom cloud deploy --provider gcp --config ./deploy/gcp-config.yaml

# Deploy to Azure
venom cloud deploy --provider azure --config ./deploy/azure-config.json
```

**Configuration File Format (JSON):**
```json
{
  "cluster_name": "venom-prod",
  "region": "us-east-1",
  "replicas": 3,
  "manifest_path": "./k8s/deployment.yaml"
}
```

#### `venom cloud status`

Check status of cloud deployments.

```bash
venom cloud status
```

**Example Output:**
```
Cloud Deployments
═══════════════════════════════════════════════════════
Provider    Status     Endpoints
───────────────────────────────────────────────────────
AWS         Running    https://venom.aws.example.com
GCP         Stopped    -
Azure       Running    https://venom.azure.example.com
═══════════════════════════════════════════════════════
```

---

### Knowledge Management

#### `venom knowledge add`

Add a document to the knowledge base.

```bash
venom knowledge add --doc <document_path> [--metadata <json_metadata>]
```

**Options:**
- `--doc` (required): Path to document file
- `--metadata` (optional): JSON metadata string

**Examples:**
```bash
# Add document without metadata
venom knowledge add --doc ./docs/guide.md

# Add document with metadata
venom knowledge add --doc ./docs/api.md --metadata '{"type":"api","version":"1.0"}'

# Add multiple documents
venom knowledge add --doc ./docs/tutorial.md --metadata '{"category":"tutorial"}'
```

#### `venom knowledge search`

Search the knowledge base.

```bash
venom knowledge search --query "<search_query>"
```

**Options:**
- `--query` (required): Search query string

**Examples:**
```bash
# Simple search
venom knowledge search --query "deployment guide"

# Complex search
venom knowledge search --query "security best practices for cloud deployment"

# Search with quotes
venom knowledge search --query "\"exact phrase\" to find"
```

**Example Output:**
```
Search Results
═══════════════════════════════════════════════════════
Rank   Score      Content
───────────────────────────────────────────────────────
1      0.945      Cloud deployment requires proper securit...
2      0.892      Security best practices include encrypti...
3      0.851      For deployment guides, refer to the clo...
═══════════════════════════════════════════════════════
```

---

### Health & Monitoring

#### `venom health check`

Run comprehensive health check.

```bash
venom health check
```

**Example Output:**
```
Health Check Results
═══════════════════════════════════════════════════════
Component             Status
───────────────────────────────────────────────────────
Core System           ✓ Healthy
Memory Usage          ✓ Healthy
CPU Load              ✓ Healthy
Disk Space            ✓ Healthy
Network               ✓ Healthy
═══════════════════════════════════════════════════════
```

#### `venom health metrics`

Display current system metrics.

```bash
venom health metrics
```

**Example Output:**
```
System Metrics
═══════════════════════════════════════════════════════
Metric                Value
───────────────────────────────────────────────────────
CPU Usage             42.3%
Memory Usage          68.5%
Available Memory      4.82 GB
Disk Usage            45.2%
Network I/O           12.5 MB/s
═══════════════════════════════════════════════════════
```

---

## Omega CLI: `venom-omega`

### Hardware & System

#### `venom-omega scan`

Scan and display hardware profile.

```bash
venom-omega scan
```

**Example Output:**
```
🌌 VENOM Ω-AIOS Universal Hardware Profile
════════════════════════════════════════════════════════
💻 CPU: 8 cores (Intel), 2800 MHz
🧠 Memory: 16.0 GB total, 12.4 GB available
🎮 GPU: CUDA (NVIDIA GeForce RTX 3080)
📐 Möbius Parameters: N=8, Λ=400.0, P=0.875
════════════════════════════════════════════════════════
```

#### `venom-omega config`

Display current configuration and capabilities.

```bash
venom-omega config
```

**Example Output:**
```
⚙️  VENOM Ω-AIOS Configuration
════════════════════════════════════════════════════════

🖥️  Hardware:
  Platform:     Linux x86_64
  CPU Cores:    8 (Intel)
  Memory:       16.0 GB
  GPU:          CUDA

📐 Möbius Engine:
  Workers (N):        8
  Lambda Wrap (Λ):    400.0
  Parallel Frac (P):  0.875
  Current Theta (θ):  0.823 [OPTIMIZE]

🚀 Estimated Performance:
  Total Speedup:      3200.0x
  840h → 0.26h
════════════════════════════════════════════════════════
```

### Temporal Compression

#### `venom-omega compress <hours>`

Calculate temporal compression estimate for a workload.

```bash
venom-omega compress <sequential_hours>
```

**Examples:**
```bash
# Calculate for 840 hours
venom-omega compress 840

# Calculate for 100 hours
venom-omega compress 100

# Calculate for custom duration
venom-omega compress 1680
```

**Example Output:**
```
⚡ Calculating temporal compression for 840.0h...

🌌 Temporal Compression Estimate
════════════════════════════════════════════════════════
Sequential Time:     840.0 hours (35.0 days)
Parallel Time:       0.26 hours (15.8 minutes)
Total Speedup:       3200.0x

Compression Breakdown:
  Theta Compression:   2.45x
  Lambda Wrap:         400.0x
  Amdahl Speedup:      3.27x
  
Mode: OPTIMIZE (θ = 0.823)
════════════════════════════════════════════════════════
```

### Performance & Monitoring

#### `venom-omega benchmark`

Run performance benchmark.

```bash
venom-omega benchmark
```

**Example Output:**
```
⚡ Running VENOM Ω-AIOS Benchmark...
════════════════════════════════════════════════════════

📊 Benchmark Results:
════════════════════════════════════════════════════════
Total Tasks:     25
Completed:       25
Failed:          0
Execution Time:  0.45s
Speedup:         55.6x
Tasks/Second:    55.6
════════════════════════════════════════════════════════
```

#### `venom-omega monitor [--duration <seconds>]`

Monitor system theta in real-time.

```bash
venom-omega monitor [--duration <seconds>]
```

**Options:**
- `--duration` (optional): Monitoring duration in seconds (default: 10)

**Examples:**
```bash
# Monitor for 10 seconds (default)
venom-omega monitor

# Monitor for 30 seconds
venom-omega monitor --duration 30

# Monitor for 1 minute
venom-omega monitor --duration 60
```

**Example Output:**
```
📊 Starting Theta Monitor for 30s...
Press Ctrl+C to stop

[00:02] θ=0.823 CPU=42.3% MEM=68.5% THERMAL=55.0°C [OPTIMIZE]
[00:04] θ=0.815 CPU=45.1% MEM=69.2% THERMAL=56.2°C [OPTIMIZE]
[00:06] θ=0.801 CPU=48.7% MEM=70.1% THERMAL=57.8°C [BALANCE]

✅ Monitoring complete
```

---

## Configuration File

### Location

- Linux/macOS: `~/.venomrc`
- Windows: `%USERPROFILE%\.venomrc`

### Format

```json
{
  "log_level": "INFO",
  "metrics_port": 8000,
  "enable_prometheus": true,
  "cloud": {
    "default_provider": "aws",
    "aws_region": "us-east-1",
    "gcp_zone": "us-central1-a",
    "azure_location": "eastus"
  },
  "security": {
    "enable_encryption": true,
    "enable_signing": true,
    "algorithm": "aes-gcm"
  },
  "knowledge": {
    "storage_path": "~/.venom/knowledge",
    "embedding_model": "sentence-transformers",
    "index_type": "faiss"
  },
  "observability": {
    "metrics_interval": 60,
    "enable_theta_monitor": true,
    "prometheus_port": 9090
  }
}
```

---

## Exit Codes

- `0`: Success
- `1`: General error
- `130`: Interrupted by user (Ctrl+C)

---

## Environment Variables

```bash
# Logging
export VENOM_LOG_LEVEL=DEBUG

# Metrics
export VENOM_METRICS_PORT=8000

# Cloud
export VENOM_CLOUD_PROVIDER=aws
export VENOM_AWS_REGION=us-east-1
export VENOM_GCP_ZONE=us-central1-a
export VENOM_AZURE_LOCATION=eastus

# Security
export VENOM_ENABLE_ENCRYPTION=true
export VENOM_ENABLE_SIGNING=true

# Paths
export VENOM_CONFIG_PATH=~/.venomrc
export VENOM_DATA_PATH=~/.venom/data
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Check system health
venom health check

# 2. Scan hardware
venom-omega scan

# 3. Train a model
venom ai train --model transformer --data ./data/train.csv

# 4. Encrypt sensitive data
venom security encrypt --file ./config/secrets.json

# 5. Deploy to cloud
venom cloud deploy --provider aws --config ./deploy/aws.json

# 6. Add documentation
venom knowledge add --doc ./docs/deployment-guide.md --metadata '{"type":"guide"}'

# 7. Monitor performance
venom-omega monitor --duration 30

# 8. Check deployment status
venom cloud status
```

---

## Tips & Best Practices

1. **Use Configuration Files**: Store common settings in `~/.venomrc`
2. **Check Health First**: Always run `venom health check` before operations
3. **Monitor Performance**: Use `venom-omega monitor` during intensive tasks
4. **Secure Keys**: Keep encryption keys separate and secure
5. **Test Locally**: Test deployments locally before cloud deployment
6. **Use Metadata**: Add meaningful metadata to knowledge base documents
7. **Regular Backups**: Back up encryption keys and important data

---

## Getting Help

- **Command Help**: `venom <command> --help`
- **Documentation**: [Full docs](.)
- **Examples**: [Code examples](examples/)
- **Issues**: [GitHub Issues](https://github.com/manuelstellian-dev/AIOS-/issues)

---

**Complete CLI reference for VENOM Framework v1.0.0**
