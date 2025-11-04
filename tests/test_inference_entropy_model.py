"""Tests for EntropyModel - Inference module"""
import pytest
import torch
from venom.inference.entropy_model import EntropyModel


def test_entropy_model_init():
    """Test EntropyModel initialization"""
    model = EntropyModel(ml_weight=0.15)
    
    assert model.ml_weight == 0.15
    assert isinstance(model.model, torch.nn.Linear)
    assert model.device is not None


def test_entropy_model_forward():
    """Test forward pass"""
    model = EntropyModel(ml_weight=0.12)
    
    x = torch.tensor([[5.0]], dtype=torch.float32)
    output = model.forward(x)
    
    assert output.shape == (1, 1)
    assert 0.0 <= output.item() <= 1.0  # Sigmoid bounds


def test_entropy_model_infer_threat():
    """Test threat inference from anomaly count"""
    model = EntropyModel(ml_weight=0.12)
    
    # Test with different anomaly counts
    threat_0 = model.infer_threat(0)
    threat_5 = model.infer_threat(5)
    threat_10 = model.infer_threat(10)
    
    assert 0.0 <= threat_0 <= 1.0
    assert 0.0 <= threat_5 <= 1.0
    assert 0.0 <= threat_10 <= 1.0
    
    # Higher anomalies should generally mean higher threat
    assert threat_10 >= threat_0


def test_entropy_model_update_weight():
    """Test weight update"""
    model = EntropyModel(ml_weight=0.12)
    
    initial_weight = model.get_weight()
    assert abs(initial_weight - 0.12) < 0.01
    
    model.update_weight(0.20)
    
    new_weight = model.get_weight()
    assert abs(new_weight - 0.20) < 0.01
    assert model.ml_weight == 0.20


def test_entropy_model_train_step():
    """Test single training step"""
    model = EntropyModel(ml_weight=0.12)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    
    # Train on one example
    loss = model.train_step(
        total_anoms=5,
        target_threat=0.7,
        optimizer=optimizer
    )
    
    assert isinstance(loss, float)
    assert loss >= 0.0  # MSE loss is always non-negative


def test_entropy_model_get_weight():
    """Test getting model weight"""
    model = EntropyModel(ml_weight=0.15)
    
    weight = model.get_weight()
    assert isinstance(weight, float)
    assert abs(weight - 0.15) < 0.01


def test_entropy_model_get_bias():
    """Test getting model bias"""
    model = EntropyModel(ml_weight=0.12)
    
    bias = model.get_bias()
    assert isinstance(bias, float)
    assert abs(bias - 0.0) < 0.01  # Initial bias is 0


def test_entropy_model_multiple_training_steps():
    """Test multiple training iterations"""
    model = EntropyModel(ml_weight=0.12)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Train for a few steps
    losses = []
    for i in range(5):
        loss = model.train_step(
            total_anoms=i + 1,
            target_threat=0.5 + (i * 0.05),
            optimizer=optimizer
        )
        losses.append(loss)
    
    # All losses should be valid
    assert all(isinstance(l, float) and l >= 0.0 for l in losses)


def test_entropy_model_device():
    """Test model is on correct device"""
    model = EntropyModel()
    
    # Model should be on CPU or CUDA
    assert model.device.type in ['cpu', 'cuda']
    
    # Model parameters should be on the same device
    for param in model.parameters():
        assert param.device == model.device
