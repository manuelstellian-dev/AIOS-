"""Tests for Vision Models Bridge"""
import pytest
import tempfile
import numpy as np
from PIL import Image
from venom.ml.vision_models import VisionModelBridge

# Suppress expected warnings for missing torch/torchvision
pytestmark = pytest.mark.filterwarnings(
    "ignore::UserWarning"
)


@pytest.fixture
def bridge():
    """Create vision bridge for testing"""
    return VisionModelBridge(device='cpu')


@pytest.fixture
def temp_image():
    """Create temporary test image"""
    img = Image.new('RGB', (224, 224), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name)
    yield temp_file.name
    # Cleanup handled by tempfile


def test_load_model(bridge):
    """Test loading a vision model"""
    if not bridge.is_available():
        pytest.skip("torch/torchvision not available")
        
    # Test loading supported model
    model = bridge.load_model('resnet50', pretrained=True)
    assert model is not None
    
    # Test caching - should return same model
    model2 = bridge.load_model('resnet50', pretrained=True)
    assert model is model2
    
    # Test unsupported model
    with pytest.raises(ValueError):
        bridge.load_model('unsupported-model')


def test_predict(bridge, temp_image):
    """Test image prediction"""
    if not bridge.is_available():
        pytest.skip("torch/torchvision not available")
        
    result = bridge.predict(temp_image, 'resnet50')
    
    assert 'image_path' in result
    assert result['image_path'] == temp_image
    assert result['model'] == 'resnet50'
    assert 'predictions' in result
    assert len(result['predictions']) == 5
    
    # Check prediction structure
    for pred in result['predictions']:
        assert 'class_id' in pred
        assert 'confidence' in pred
        assert isinstance(pred['class_id'], int)
        assert 0.0 <= pred['confidence'] <= 1.0


def test_batch_predict(bridge, temp_image):
    """Test batch image prediction"""
    if not bridge.is_available():
        pytest.skip("torch/torchvision not available")
        
    # Create multiple image paths (using same image for simplicity)
    image_paths = [temp_image, temp_image, temp_image]
    
    results = bridge.batch_predict(image_paths, 'resnet50')
    
    assert len(results) == 3
    for result in results:
        assert 'predictions' in result
        assert len(result['predictions']) == 5


def test_extract_features(bridge, temp_image):
    """Test feature extraction"""
    if not bridge.is_available():
        pytest.skip("torch/torchvision not available")
        
    features = bridge.extract_features(temp_image, 'resnet50')
    
    assert isinstance(features, np.ndarray)
    assert features.ndim == 1  # Should be 1D feature vector
    assert len(features) > 0
    
    # Test with different models
    features_efficient = bridge.extract_features(temp_image, 'efficientnet_b0')
    assert isinstance(features_efficient, np.ndarray)
    
    features_mobile = bridge.extract_features(temp_image, 'mobilenet_v2')
    assert isinstance(features_mobile, np.ndarray)


def test_device_detection():
    """Test device detection"""
    # Test auto device detection
    bridge_auto = VisionModelBridge(device='auto')
    assert bridge_auto.get_device() in ['cpu', 'cuda']
    
    # Test explicit CPU
    bridge_cpu = VisionModelBridge(device='cpu')
    assert bridge_cpu.get_device() == 'cpu'
    
    # Test graceful fallback when torch not available
    if not bridge_auto.is_available():
        assert bridge_auto.get_device() == 'cpu'
