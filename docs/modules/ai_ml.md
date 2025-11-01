# AI & Machine Learning Module

The AI/ML module provides comprehensive machine learning capabilities including AutoML, model serving, and support for various model architectures.

## Components

### AutoML Pipeline

Automated hyperparameter tuning using Optuna.

```python
from venom.ml import AutoMLPipeline

# Initialize pipeline
pipeline = AutoMLPipeline(framework='optuna')

# Define objective function
def objective(trial):
    lr = trial.suggest_float('lr', 0.001, 0.1, log=True)
    n_layers = trial.suggest_int('n_layers', 2, 10)
    
    # Train model and return metric
    accuracy = train_model(lr=lr, n_layers=n_layers)
    return accuracy

# Run optimization
best_params = pipeline.tune_hyperparameters(
    objective_fn=objective,
    search_space={'lr': (0.001, 0.1), 'n_layers': (2, 10)},
    n_trials=100,
    direction='maximize'
)
```

### Model Serving

Serve trained models via REST API.

```python
from venom.ml import ModelServer

# Initialize server
server = ModelServer(port=8080)

# Load model
server.load_model('my_model', './models/model.pt')

# Start serving
server.start()
```

### Model Registry

Version control and management for models.

```python
from venom.ml import ModelRegistry

# Initialize registry
registry = ModelRegistry(storage_path='./models')

# Register model
registry.register_model(
    name='classifier_v1',
    model_path='./trained/model.pt',
    metadata={
        'accuracy': 0.95,
        'framework': 'pytorch',
        'created_at': '2024-11-01'
    }
)

# List models
models = registry.list_models()

# Load model
model = registry.load_model('classifier_v1', version='latest')
```

### Transformer Bridge

Integration with HuggingFace transformers.

```python
from venom.ml import TransformerBridge

# Initialize bridge
bridge = TransformerBridge(model_name='gpt2')

# Generate text
output = bridge.generate_text("Once upon a time", max_length=100)

# Fine-tune on custom data
bridge.fine_tune(train_data, epochs=3)
```

### Vision Models

Computer vision models for classification and detection.

```python
from venom.ml import VisionModels
from PIL import Image

# Initialize vision model
vision = VisionModels(model_name='resnet50')

# Load and classify image
image = Image.open('photo.jpg')
predictions = vision.classify_image(image)

for pred in predictions:
    print(f"{pred['label']}: {pred['confidence']:.2%}")
```

## CLI Usage

```bash
# Train a model
venom ai train --model transformer --data ./data/train.csv

# Run prediction
venom ai predict --model ./models/model.pt --input "sample text"
```

## Configuration

Add to `~/.venomrc`:

```json
{
  "ml": {
    "default_framework": "pytorch",
    "model_storage": "~/.venom/models",
    "automl": {
      "n_trials": 100,
      "timeout": 3600
    },
    "serving": {
      "port": 8080,
      "workers": 4
    }
  }
}
```

## Examples

See [examples/ml/](../examples/) for complete examples.

## API Reference

Full API documentation available at [docs/api/ml.md](../api/ml.md).
