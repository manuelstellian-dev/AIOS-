# VENOM Examples

This directory contains example code demonstrating VENOM Framework capabilities.

## Available Examples

### Basic Examples

- **basic_example.py**: Complete basic example showing core components
  - Arbiter initialization
  - T_Λ Pulse configuration
  - PID controller
  - Entropy model
  - Immutable ledger

### AI/ML Examples

```python
# AutoML Example
from venom.ml import AutoMLPipeline

pipeline = AutoMLPipeline(framework='optuna')
best_params = pipeline.tune_hyperparameters(
    objective_fn=my_objective,
    search_space={'lr': (0.001, 0.1)},
    n_trials=100
)
```

### Security Examples

```python
# Encryption Example
from venom.security import AdvancedEncryption

encryption = AdvancedEncryption(algorithm='aes-gcm')
key = encryption.generate_key(algorithm='aes-gcm')
encrypted = encryption.encrypt(b"secret data", key)
decrypted = encryption.decrypt(encrypted, key)
```

### Cloud Examples

```python
# AWS Deployment Example
from venom.cloud.aws import EKSDeployer

deployer = EKSDeployer("venom-prod", "us-east-1")
deployer.deploy("./k8s/deployment.yaml")
```

### Knowledge Examples

```python
# Knowledge Base Example
from venom.knowledge import DocumentStore, SemanticSearch

store = DocumentStore()
doc_id = store.add_document("VENOM documentation", {"type": "docs"})

search = SemanticSearch()
results = search.search("deployment guide", top_k=5)
```

## Running Examples

```bash
# Run basic example
python docs/examples/basic_example.py

# Run with specific module
python -m docs.examples.basic_example
```

## Example Structure

Each example includes:
- Initialization code
- Core functionality demonstration
- Error handling
- Output explanation
- Cleanup (if needed)

## Contributing Examples

To add a new example:

1. Create a new file in this directory
2. Follow the existing code style
3. Add docstrings and comments
4. Include example output
5. Update this README

## More Examples

For more examples, see:
- [Quick Start Guide](../quickstart.md)
- [Module Documentation](../modules/)
- [API Reference](../api/)

---

**Happy coding with VENOM! 🚀**
