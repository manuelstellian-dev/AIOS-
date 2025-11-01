"""Tests for Model Registry"""
import pytest
import tempfile
import shutil
from pathlib import Path
from venom.ml.registry import ModelRegistry


@pytest.fixture
def temp_registry():
    """Create temporary registry for testing"""
    temp_dir = tempfile.mkdtemp()
    registry = ModelRegistry(storage_path=temp_dir)
    yield registry
    shutil.rmtree(temp_dir)


def test_register_model(temp_registry):
    """Test registering a model"""
    registry = temp_registry
    
    metadata = {
        'framework': 'pytorch',
        'architecture': 'resnet50',
        'input_shape': [3, 224, 224]
    }
    
    result = registry.register_model(
        name='test_model',
        version='1.0.0',
        metadata=metadata,
        model_path='/tmp/test_model.pth'
    )
    
    assert result['name'] == 'test_model'
    assert result['version'] == '1.0.0'
    assert 'checksum' in result
    assert 'registered_at' in result
    
    # Verify model is in registry
    assert 'test_model' in registry.list_models()


def test_get_model_latest_version(temp_registry):
    """Test getting latest version of a model"""
    registry = temp_registry
    
    # Register multiple versions
    registry.register_model(
        name='test_model',
        version='1.0.0',
        metadata={'notes': 'initial'},
        model_path='/tmp/model_v1.pth'
    )
    
    registry.register_model(
        name='test_model',
        version='2.0.0',
        metadata={'notes': 'improved'},
        model_path='/tmp/model_v2.pth'
    )
    
    # Get latest version (should be 2.0.0)
    latest = registry.get_model('test_model')
    assert latest['version'] == '2.0.0'
    assert latest['metadata']['notes'] == 'improved'
    
    # Get specific version
    v1 = registry.get_model('test_model', version='1.0.0')
    assert v1['version'] == '1.0.0'
    assert v1['metadata']['notes'] == 'initial'


def test_list_models(temp_registry):
    """Test listing all models"""
    registry = temp_registry
    
    # Register multiple models
    registry.register_model('model_a', '1.0.0', {}, '/tmp/a.pth')
    registry.register_model('model_b', '1.0.0', {}, '/tmp/b.pth')
    registry.register_model('model_c', '1.0.0', {}, '/tmp/c.pth')
    
    models = registry.list_models()
    assert len(models) == 3
    assert 'model_a' in models
    assert 'model_b' in models
    assert 'model_c' in models
    
    # Test list_versions
    registry.register_model('model_a', '2.0.0', {}, '/tmp/a2.pth')
    versions = registry.list_versions('model_a')
    assert len(versions) == 2
    assert '1.0.0' in versions
    assert '2.0.0' in versions


def test_track_performance(temp_registry):
    """Test tracking model performance metrics"""
    registry = temp_registry
    
    registry.register_model('test_model', '1.0.0', {}, '/tmp/model.pth')
    
    # Track performance
    metrics = {
        'accuracy': 0.95,
        'f1_score': 0.93,
        'precision': 0.96
    }
    registry.track_performance('test_model', '1.0.0', metrics)
    
    # Verify metrics are stored
    model = registry.get_model('test_model', '1.0.0')
    assert model['performance_metrics']['accuracy'] == 0.95
    assert model['performance_metrics']['f1_score'] == 0.93
    assert 'last_metric_update' in model


def test_get_best_model(temp_registry):
    """Test getting best model based on metric"""
    registry = temp_registry
    
    # Register multiple versions with different performance
    registry.register_model('test_model', '1.0.0', {}, '/tmp/v1.pth')
    registry.track_performance('test_model', '1.0.0', {'accuracy': 0.85})
    
    registry.register_model('test_model', '2.0.0', {}, '/tmp/v2.pth')
    registry.track_performance('test_model', '2.0.0', {'accuracy': 0.92})
    
    registry.register_model('test_model', '3.0.0', {}, '/tmp/v3.pth')
    registry.track_performance('test_model', '3.0.0', {'accuracy': 0.88})
    
    # Get best model by accuracy
    best = registry.get_best_model('test_model', metric='accuracy')
    assert best['version'] == '2.0.0'
    assert best['performance_metrics']['accuracy'] == 0.92
    
    # Test with non-existent metric
    with pytest.raises(ValueError):
        registry.get_best_model('test_model', metric='non_existent')
