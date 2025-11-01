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
