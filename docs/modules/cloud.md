# Cloud Deployment Module

The Cloud module provides unified interface for deploying to major cloud providers.

## Supported Providers

- **AWS** (Amazon Web Services)
- **GCP** (Google Cloud Platform)
- **Azure** (Microsoft Azure)

## Components

### AWS Deployment

#### EKS Deployer

Deploy to Amazon Elastic Kubernetes Service.

```python
from venom.cloud.aws import EKSDeployer

# Initialize deployer
deployer = EKSDeployer(
    cluster_name="venom-prod",
    region="us-east-1"
)

# Get cluster configuration
config = deployer.get_deployment_config()

# Deploy application
deployer.deploy(manifest_path="./k8s/deployment.yaml")
```

#### S3 Backup

Backup data to Amazon S3.

```python
from venom.cloud.aws import S3Backup

# Initialize backup
backup = S3Backup(bucket_name="venom-backups", region="us-east-1")

# Upload file
backup.upload_file("./data/important.db", "backups/important.db")

# Download file
backup.download_file("backups/important.db", "./restore/important.db")
```

#### Lambda Handler

Deploy serverless functions.

```python
from venom.cloud.aws import LambdaHandler

# Initialize handler
handler = LambdaHandler(function_name="venom-processor", region="us-east-1")

# Deploy function
handler.deploy(
    code_path="./functions/processor.py",
    handler="processor.lambda_handler",
    runtime="python3.10"
)

# Invoke function
result = handler.invoke(payload={"key": "value"})
```

### GCP Deployment

#### GKE Deployer

Deploy to Google Kubernetes Engine.

```python
from venom.cloud.gcp import GKEDeployer

# Initialize deployer
deployer = GKEDeployer(
    cluster_name="venom-prod",
    zone="us-central1-a",
    project="my-project"
)

# Deploy application
deployer.deploy(manifest_path="./k8s/deployment.yaml")
```

#### Cloud Storage

Store data in Google Cloud Storage.

```python
from venom.cloud.gcp import StorageBackup

# Initialize storage
storage = StorageBackup(bucket_name="venom-backups")

# Upload blob
storage.upload_blob("./data/file.txt", "backups/file.txt")

# Download blob
storage.download_blob("backups/file.txt", "./restore/file.txt")
```

#### Cloud Functions

Deploy serverless functions.

```python
from venom.cloud.gcp import CloudFunctionHandler

# Initialize handler
handler = CloudFunctionHandler(function_name="venom-processor")

# Deploy function
handler.deploy(
    source_dir="./functions",
    entry_point="process",
    runtime="python310"
)
```

### Azure Deployment

#### AKS Deployer

Deploy to Azure Kubernetes Service.

```python
from venom.cloud.azure import AKSDeployer

# Initialize deployer
deployer = AKSDeployer(
    cluster_name="venom-prod",
    resource_group="venom-rg",
    location="eastus"
)

# Deploy application
deployer.deploy(manifest_path="./k8s/deployment.yaml")
```

#### Blob Storage

Store data in Azure Blob Storage.

```python
from venom.cloud.azure import BlobBackup

# Initialize storage
storage = BlobBackup(
    container_name="venom-backups",
    storage_account="venomstore"
)

# Upload blob
storage.upload_blob("./data/file.txt", "backups/file.txt")

# Download blob
storage.download_blob("backups/file.txt", "./restore/file.txt")
```

#### Azure Functions

Deploy serverless functions.

```python
from venom.cloud.azure import FunctionHandler

# Initialize handler
handler = FunctionHandler(
    function_app="venom-processor",
    resource_group="venom-rg"
)

# Deploy function
handler.deploy(
    source_dir="./functions",
    function_name="process"
)
```

## CLI Usage

```bash
# Deploy to AWS
venom cloud deploy --provider aws --config ./deploy/aws.json

# Deploy to GCP
venom cloud deploy --provider gcp --config ./deploy/gcp.yaml

# Deploy to Azure
venom cloud deploy --provider azure --config ./deploy/azure.json

# Check deployment status
venom cloud status
```

## Configuration Examples

### AWS Configuration (`aws.json`)

```json
{
  "provider": "aws",
  "cluster_name": "venom-prod",
  "region": "us-east-1",
  "manifest_path": "./k8s/deployment.yaml",
  "replicas": 3,
  "instance_type": "t3.medium"
}
```

### GCP Configuration (`gcp.yaml`)

```yaml
provider: gcp
cluster_name: venom-prod
zone: us-central1-a
project: my-project-id
manifest_path: ./k8s/deployment.yaml
replicas: 3
machine_type: n1-standard-2
```

### Azure Configuration (`azure.json`)

```json
{
  "provider": "azure",
  "cluster_name": "venom-prod",
  "resource_group": "venom-rg",
  "location": "eastus",
  "manifest_path": "./k8s/deployment.yaml",
  "replicas": 3,
  "vm_size": "Standard_D2s_v3"
}
```

## Multi-Cloud Strategy

Deploy to multiple clouds for redundancy:

```python
from venom.cloud.aws import EKSDeployer as AWSDeployer
from venom.cloud.gcp import GKEDeployer as GCPDeployer
from venom.cloud.azure import AKSDeployer as AzureDeployer

# Deploy to all three clouds
providers = [
    AWSDeployer("venom-prod", "us-east-1"),
    GCPDeployer("venom-prod", "us-central1-a"),
    AzureDeployer("venom-prod", "venom-rg", "eastus")
]

for deployer in providers:
    deployer.deploy("./k8s/deployment.yaml")
```

## Environment Variables

```bash
# AWS
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# GCP
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export GCP_PROJECT=my-project-id

# Azure
export AZURE_SUBSCRIPTION_ID=your_subscription
export AZURE_TENANT_ID=your_tenant
export AZURE_CLIENT_ID=your_client
export AZURE_CLIENT_SECRET=your_secret
```

## Best Practices

1. **Use Infrastructure as Code**: Store configurations in version control
2. **Implement Blue-Green Deployments**: Zero-downtime deployments
3. **Enable Auto-Scaling**: Scale based on demand
4. **Monitor Resources**: Track costs and usage
5. **Backup Regularly**: Automated backups to cloud storage
6. **Use Secrets Management**: Never hardcode credentials

## Examples

See [examples/cloud/](../examples/) for complete examples.

## API Reference

Full API documentation available at [docs/api/cloud.md](../api/cloud.md).
