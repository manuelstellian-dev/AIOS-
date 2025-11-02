"""Tests for Transformer Bridge"""
import pytest
from venom.ml.transformer_bridge import TransformerBridge


@pytest.fixture
def bridge():
    """Create transformer bridge for testing"""
    return TransformerBridge()


def test_load_model(bridge):
    """Test loading a transformer model"""
    if not bridge.is_available():
        pytest.skip("transformers not available")
        
    # Test loading a supported model (using tiny model for fast testing)
    model = bridge.load_model('sshleifer/tiny-gpt2', task='text-generation')
    assert model is not None
    
    # Test caching - should return same pipeline
    model2 = bridge.load_model('sshleifer/tiny-gpt2', task='text-generation')
    assert model is model2
    
    # Test unsupported model
    with pytest.raises(ValueError):
        bridge.load_model('unsupported-model', task='text-generation')
        
    # Test unsupported task
    with pytest.raises(ValueError):
        bridge.load_model('sshleifer/tiny-gpt2', task='unsupported-task')


def test_inference(bridge):
    """Test single inference"""
    if not bridge.is_available():
        pytest.skip("transformers not available")
        
    text = "Hello, how are you"
    result = bridge.inference(
        model_name='sshleifer/tiny-gpt2',
        text=text,
        task='text-generation',
        max_length=20
    )
    
    assert 'input' in result
    assert result['input'] == text
    assert 'output' in result
    assert result['model'] == 'sshleifer/tiny-gpt2'
    assert result['task'] == 'text-generation'


def test_batch_inference(bridge):
    """Test batch inference"""
    if not bridge.is_available():
        pytest.skip("transformers not available")
        
    texts = [
        "Hello, how are you",
        "The weather is nice today",
        "Machine learning is interesting"
    ]
    
    results = bridge.batch_inference(
        model_name='sshleifer/tiny-gpt2',
        texts=texts,
        task='text-generation',
        max_length=20
    )
    
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result['input'] == texts[i]
        assert 'output' in result
        assert result['model'] == 'sshleifer/tiny-gpt2'


def test_list_models(bridge):
    """Test listing available models"""
    models = bridge.list_available_models()
    
    assert isinstance(models, list)
    assert len(models) > 0
    assert 'sshleifer/tiny-gpt2' in models
    assert 'prajjwal1/bert-tiny' in models
    assert 't5-small' in models


def test_graceful_fallback():
    """Test graceful fallback when transformers not installed"""
    bridge = TransformerBridge()
    
    if bridge.is_available():
        pytest.skip("transformers is available, cannot test fallback")
        
    # Should not raise during initialization
    assert not bridge.is_available()
    
    # Should raise when trying to use
    with pytest.raises(RuntimeError):
        bridge.load_model('sshleifer/tiny-gpt2')
        
    with pytest.raises(RuntimeError):
        bridge.inference("test", 'sshleifer/tiny-gpt2')
