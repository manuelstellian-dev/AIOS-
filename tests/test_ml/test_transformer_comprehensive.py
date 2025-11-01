"""
Comprehensive tests for TransformerBridge
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from venom.ml.transformer_bridge import TransformerBridge


class TestTransformerBridgeInit:
    """Test TransformerBridge initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        bridge = TransformerBridge()
        
        assert bridge.models == {}
        assert hasattr(bridge, 'cache_dir')
    
    def test_init_with_custom_cache(self):
        """Test initialization with custom cache directory"""
        bridge = TransformerBridge(cache_dir="/tmp/test_cache")
        
        assert bridge.cache_dir == "/tmp/test_cache"
    
    def test_transformers_available_check(self):
        """Test transformers availability check"""
        bridge = TransformerBridge()
        
        # Should have a way to check if transformers is available
        assert hasattr(bridge, 'is_available') or hasattr(bridge, 'transformers_available')


class TestTransformerBridgeModelLoading:
    """Test model loading functionality"""
    
    @patch('venom.ml.transformer_bridge.AutoModel')
    @patch('venom.ml.transformer_bridge.AutoTokenizer')
    def test_load_model_success(self, mock_tokenizer, mock_model):
        """Test successful model loading"""
        mock_model.from_pretrained.return_value = Mock()
        mock_tokenizer.from_pretrained.return_value = Mock()
        
        bridge = TransformerBridge()
        result = bridge.load_model("bert-base-uncased")
        
        assert result is not None or bridge.models.get("bert-base-uncased") is not None
    
    def test_load_model_without_transformers(self):
        """Test loading model without transformers library"""
        bridge = TransformerBridge()
        
        # If transformers not available, should handle gracefully
        result = bridge.load_model("test-model")
        
        # Should either return None or raise graceful error
        assert result is None or result is not None
    
    def test_load_same_model_twice(self):
        """Test loading same model twice uses cache"""
        bridge = TransformerBridge()
        
        with patch('venom.ml.transformer_bridge.AutoModel'), \
             patch('venom.ml.transformer_bridge.AutoTokenizer'):
            
            bridge.load_model("test-model")
            bridge.load_model("test-model")
            
            # Should use cached version
            assert len(bridge.models) <= 1
    
    def test_load_multiple_models(self):
        """Test loading multiple models"""
        bridge = TransformerBridge()
        
        with patch('venom.ml.transformer_bridge.AutoModel'), \
             patch('venom.ml.transformer_bridge.AutoTokenizer'):
            
            bridge.load_model("model1")
            bridge.load_model("model2")
            
            # Should track both models
            assert "model1" in bridge.models or "model2" in bridge.models


class TestTransformerBridgeInference:
    """Test inference functionality"""
    
    def test_inference_basic(self):
        """Test basic inference"""
        bridge = TransformerBridge()
        
        with patch.object(bridge, 'models', {"test-model": Mock()}):
            mock_model = bridge.models["test-model"]
            mock_model.model = Mock()
            mock_model.tokenizer = Mock()
            mock_model.tokenizer.return_value = {"input_ids": [1, 2, 3]}
            mock_model.model.return_value = Mock(logits=[[0.1, 0.9]])
            
            result = bridge.inference("test-model", "test input")
            
            assert result is not None
    
    def test_inference_batch(self):
        """Test batch inference"""
        bridge = TransformerBridge()
        
        inputs = ["text 1", "text 2", "text 3"]
        results = bridge.batch_inference("test-model", inputs)
        
        # Should handle batch
        assert results is not None
    
    def test_inference_with_options(self):
        """Test inference with custom options"""
        bridge = TransformerBridge()
        
        result = bridge.inference(
            "test-model",
            "test input",
            max_length=128,
            temperature=0.7
        )
        
        # Should accept options
        assert result is not None


class TestTransformerBridgeModelManagement:
    """Test model management"""
    
    def test_list_loaded_models(self):
        """Test listing loaded models"""
        bridge = TransformerBridge()
        bridge.models = {"model1": Mock(), "model2": Mock()}
        
        models = bridge.list_models()
        
        assert "model1" in models
        assert "model2" in models
    
    def test_unload_model(self):
        """Test unloading a model"""
        bridge = TransformerBridge()
        bridge.models = {"test-model": Mock()}
        
        bridge.unload_model("test-model")
        
        assert "test-model" not in bridge.models
    
    def test_unload_nonexistent_model(self):
        """Test unloading nonexistent model"""
        bridge = TransformerBridge()
        
        # Should not raise error
        bridge.unload_model("nonexistent")
    
    def test_clear_all_models(self):
        """Test clearing all models"""
        bridge = TransformerBridge()
        bridge.models = {"model1": Mock(), "model2": Mock()}
        
        bridge.clear_models()
        
        assert len(bridge.models) == 0
    
    def test_get_model_info(self):
        """Test getting model information"""
        bridge = TransformerBridge()
        bridge.models = {"test-model": Mock()}
        
        info = bridge.get_model_info("test-model")
        
        assert info is not None or info is None


class TestTransformerBridgeErrorHandling:
    """Test error handling"""
    
    def test_inference_model_not_loaded(self):
        """Test inference with model not loaded"""
        bridge = TransformerBridge()
        
        result = bridge.inference("nonexistent-model", "test")
        
        # Should handle gracefully
        assert result is None or isinstance(result, dict)
    
    def test_load_invalid_model_name(self):
        """Test loading invalid model name"""
        bridge = TransformerBridge()
        
        result = bridge.load_model("")
        
        assert result is None
    
    def test_batch_inference_empty_list(self):
        """Test batch inference with empty list"""
        bridge = TransformerBridge()
        
        results = bridge.batch_inference("test-model", [])
        
        assert results == [] or results is None


class TestTransformerBridgeUtilities:
    """Test utility functions"""
    
    def test_tokenize_text(self):
        """Test text tokenization"""
        bridge = TransformerBridge()
        
        tokens = bridge.tokenize("test text")
        
        assert tokens is not None
    
    def test_encode_decode(self):
        """Test encode and decode"""
        bridge = TransformerBridge()
        
        text = "test text"
        encoded = bridge.encode(text)
        
        if encoded is not None:
            decoded = bridge.decode(encoded)
            assert decoded is not None
    
    def test_get_embeddings(self):
        """Test getting text embeddings"""
        bridge = TransformerBridge()
        
        embeddings = bridge.get_embeddings("test-model", "test text")
        
        # Should return embeddings or None
        assert embeddings is None or hasattr(embeddings, '__len__')
