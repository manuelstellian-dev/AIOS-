"""
Transformer Bridge - HuggingFace transformers integration
Provides unified interface for transformer models and inference
"""
from typing import Dict, Any, List, Optional
import warnings


class TransformerBridge:
    """
    Bridge to HuggingFace transformers library
    Supports text-generation, text-classification, question-answering, summarization
    """
    
    # Supported models
    SUPPORTED_MODELS = [
        'bert-base-uncased',
        'gpt2',
        't5-small',
        'distilbert-base-uncased',
        'roberta-base'
    ]
    
    # Supported tasks
    SUPPORTED_TASKS = [
        'text-generation',
        'text-classification',
        'question-answering',
        'summarization'
    ]
    
    def __init__(self, cache_dir: str = './models/transformers'):
        """
        Initialize transformer bridge
        
        Args:
            cache_dir: Directory to cache downloaded models
        """
        self.cache_dir = cache_dir
        self._model_cache = {}
        self._pipeline_cache = {}
        self.models = {}  # Public models dict for test compatibility
        
        # Check if transformers is available
        try:
            import transformers
            self.transformers_available = True
            self.transformers = transformers
        except ImportError:
            self.transformers_available = False
            self.transformers = None
            warnings.warn(
                "transformers library not available. "
                "Install with: pip install transformers"
            )
            
    def _check_availability(self):
        """Check if transformers is available, raise error if not"""
        if not self.transformers_available:
            raise RuntimeError(
                "transformers library not installed. "
                "Install with: pip install transformers"
            )
            
    def load_model(self, model_name: str, task: str = 'text-generation') -> Any:
        """
        Load a transformer model for a specific task
        
        Args:
            model_name: Name of the model (e.g., 'gpt2', 'bert-base-uncased')
            task: Task type (text-generation, text-classification, etc.)
            
        Returns:
            Loaded model pipeline
            
        Raises:
            RuntimeError: If transformers not installed
            ValueError: If model or task not supported
        """
        self._check_availability()
        
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Model '{model_name}' not supported. "
                f"Supported models: {self.SUPPORTED_MODELS}"
            )
            
        if task not in self.SUPPORTED_TASKS:
            raise ValueError(
                f"Task '{task}' not supported. "
                f"Supported tasks: {self.SUPPORTED_TASKS}"
            )
            
        cache_key = f"{model_name}:{task}"
        
        # Return cached pipeline if available
        if cache_key in self._pipeline_cache:
            return self._pipeline_cache[cache_key]
            
        # Load pipeline
        try:
            pipeline = self.transformers.pipeline(
                task=task,
                model=model_name,
                cache_dir=self.cache_dir
            )
            self._pipeline_cache[cache_key] = pipeline
            # Also track in public models dict for test compatibility
            self.models[model_name] = pipeline
            return pipeline
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model '{model_name}' for task '{task}': {e}"
            )
            
    def inference(self, text: str, model_name: str, 
                 task: str = 'text-generation', **kwargs) -> Dict[str, Any]:
        """
        Run inference on a single text input
        
        Args:
            text: Input text
            model_name: Name of the model to use
            task: Task type
            **kwargs: Additional arguments passed to pipeline
            
        Returns:
            Dictionary with inference results
            
        Raises:
            RuntimeError: If transformers not installed
        """
        self._check_availability()
        
        pipeline = self.load_model(model_name, task)
        
        # Set default parameters based on task
        if task == 'text-generation':
            kwargs.setdefault('max_length', 50)
            kwargs.setdefault('num_return_sequences', 1)
        elif task == 'summarization':
            kwargs.setdefault('max_length', 130)
            kwargs.setdefault('min_length', 30)
            
        try:
            result = pipeline(text, **kwargs)
            
            return {
                'input': text,
                'output': result,
                'model': model_name,
                'task': task
            }
        except Exception as e:
            return {
                'input': text,
                'error': str(e),
                'model': model_name,
                'task': task
            }
            
    def batch_inference(self, texts: List[str], model_name: str,
                       task: str = 'text-generation', **kwargs) -> List[Dict[str, Any]]:
        """
        Run inference on multiple text inputs
        
        Args:
            texts: List of input texts
            model_name: Name of the model to use
            task: Task type
            **kwargs: Additional arguments passed to pipeline
            
        Returns:
            List of dictionaries with inference results
            
        Raises:
            RuntimeError: If transformers not installed
        """
        self._check_availability()
        
        pipeline = self.load_model(model_name, task)
        
        # Set default parameters based on task
        if task == 'text-generation':
            kwargs.setdefault('max_length', 50)
            kwargs.setdefault('num_return_sequences', 1)
        elif task == 'summarization':
            kwargs.setdefault('max_length', 130)
            kwargs.setdefault('min_length', 30)
            
        results = []
        for text in texts:
            try:
                result = pipeline(text, **kwargs)
                results.append({
                    'input': text,
                    'output': result,
                    'model': model_name,
                    'task': task
                })
            except Exception as e:
                results.append({
                    'input': text,
                    'error': str(e),
                    'model': model_name,
                    'task': task
                })
                
        return results
        
    def list_available_models(self) -> List[str]:
        """
        List all available/supported models
        
        Returns:
            List of model names
        """
        return self.SUPPORTED_MODELS.copy()
        
    def is_available(self) -> bool:
        """
        Check if transformers library is available
        
        Returns:
            True if transformers is installed, False otherwise
        """
        return self.transformers_available
    
    def tokenize(self, text: str, model_name: Optional[str] = None, **kwargs) -> Optional[List[int]]:
        """
        Tokenize text into tokens
        
        Args:
            text: Input text to tokenize
            model_name: Optional model name to use for tokenization (defaults to 'bert-base-uncased')
            **kwargs: Additional arguments passed to tokenizer
            
        Returns:
            List of token IDs, or None if transformers not available
        """
        if not self.transformers_available:
            return None
            
        try:
            # Use default model if not specified
            if model_name is None:
                model_name = 'bert-base-uncased'
            
            # Load tokenizer
            tokenizer = self.transformers.AutoTokenizer.from_pretrained(
                model_name, 
                cache_dir=self.cache_dir
            )
            
            # Tokenize
            tokens = tokenizer.encode(text, **kwargs)
            return tokens
        except Exception as e:
            warnings.warn(f"Tokenization failed: {e}")
            return None
    
    def encode(self, text: str, model_name: Optional[str] = None, **kwargs) -> Optional[List[int]]:
        """
        Encode text to token IDs
        
        Args:
            text: Input text to encode
            model_name: Optional model name to use (defaults to 'bert-base-uncased')
            **kwargs: Additional arguments passed to tokenizer
            
        Returns:
            List of token IDs, or None if transformers not available
        """
        return self.tokenize(text, model_name, **kwargs)
    
    def decode(self, tokens: List[int], model_name: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Decode token IDs back to text
        
        Args:
            tokens: List of token IDs to decode
            model_name: Optional model name to use (defaults to 'bert-base-uncased')
            **kwargs: Additional arguments passed to tokenizer
            
        Returns:
            Decoded text string, or None if transformers not available
        """
        if not self.transformers_available:
            return None
            
        try:
            # Use default model if not specified
            if model_name is None:
                model_name = 'bert-base-uncased'
            
            # Load tokenizer
            tokenizer = self.transformers.AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            # Decode
            text = tokenizer.decode(tokens, **kwargs)
            return text
        except Exception as e:
            warnings.warn(f"Decoding failed: {e}")
            return None
    
    def get_embeddings(self, model_name: str, text: str, **kwargs) -> Optional[Any]:
        """
        Get text embeddings from a model
        
        Args:
            model_name: Name of the model to use
            text: Input text
            **kwargs: Additional arguments
            
        Returns:
            Text embeddings as numpy array/tensor, or None if not available
        """
        if not self.transformers_available:
            return None
            
        try:
            import torch
            
            # Load model and tokenizer
            tokenizer = self.transformers.AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            model = self.transformers.AutoModel.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", **kwargs)
            
            # Get embeddings
            with torch.no_grad():
                outputs = model(**inputs)
                # Check if model has last_hidden_state attribute
                if hasattr(outputs, 'last_hidden_state'):
                    embeddings = outputs.last_hidden_state
                elif hasattr(outputs, 'pooler_output'):
                    embeddings = outputs.pooler_output
                else:
                    # Fallback to first element if it's a tuple/list
                    embeddings = outputs[0] if isinstance(outputs, (tuple, list)) else outputs
            
            # Return as numpy array
            return embeddings.numpy()
        except Exception as e:
            warnings.warn(f"Failed to get embeddings: {e}")
            return None
    
    def list_models(self) -> List[str]:
        """
        List all currently loaded models
        
        Returns:
            List of loaded model names
        """
        return list(self.models.keys())
    
    def unload_model(self, model_name: str) -> None:
        """
        Unload a specific model from memory
        
        Args:
            model_name: Name of the model to unload
        """
        if model_name in self.models:
            del self.models[model_name]
        
        # Also clean up from internal caches - use dict comprehension for efficiency
        self._pipeline_cache = {
            k: v for k, v in self._pipeline_cache.items() 
            if not k.startswith(f"{model_name}:")
        }
    
    def clear_models(self) -> None:
        """
        Clear all loaded models from memory
        """
        self.models.clear()
        self._model_cache.clear()
        self._pipeline_cache.clear()
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a loaded model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information, or None if model not loaded
        """
        if model_name in self.models:
            return {
                'name': model_name,
                'loaded': True,
                'cache_dir': self.cache_dir
            }
        return None
