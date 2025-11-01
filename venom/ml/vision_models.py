"""
Vision Models Bridge - Computer vision models integration
Supports ResNet, EfficientNet, MobileNet for image classification
"""
import warnings
from typing import Dict, Any, List, Optional
import numpy as np


class VisionModelBridge:
    """
    Bridge to computer vision models (torchvision)
    Supports ResNet50, EfficientNet-B0, MobileNet-V2
    """
    
    # Supported models
    SUPPORTED_MODELS = [
        'resnet50',
        'efficientnet_b0',
        'mobilenet_v2'
    ]
    
    # ImageNet normalization statistics
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]
    
    def __init__(self, device: str = 'auto'):
        """
        Initialize vision model bridge
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        self._model_cache = {}
        self._preprocess_cache = {}
        
        # Check availability
        try:
            import torch
            import torchvision
            from torchvision import transforms
            from PIL import Image
            
            self.torch_available = True
            self.torch = torch
            self.torchvision = torchvision
            self.transforms = transforms
            self.Image = Image
            
            # Determine device
            if device == 'auto':
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            else:
                self.device = device
                
        except ImportError:
            self.torch_available = False
            self.torch = None
            self.torchvision = None
            self.transforms = None
            self.Image = None
            self.device = 'cpu'
            warnings.warn(
                "torch/torchvision not available. "
                "Install with: pip install torch torchvision"
            )
            
    def _check_availability(self):
        """Check if torch/torchvision is available"""
        if not self.torch_available:
            raise RuntimeError(
                "torch/torchvision not installed. "
                "Install with: pip install torch torchvision"
            )
            
    def _get_preprocess_transform(self):
        """
        Get preprocessing transform for ImageNet models
        
        Returns:
            Torchvision transforms composition
        """
        if 'default' in self._preprocess_cache:
            return self._preprocess_cache['default']
            
        transform = self.transforms.Compose([
            self.transforms.Resize(256),
            self.transforms.CenterCrop(224),
            self.transforms.ToTensor(),
            self.transforms.Normalize(
                mean=self.IMAGENET_MEAN,
                std=self.IMAGENET_STD
            )
        ])
        
        self._preprocess_cache['default'] = transform
        return transform
        
    def load_model(self, model_name: str, pretrained: bool = True) -> Any:
        """
        Load a vision model
        
        Args:
            model_name: Name of the model ('resnet50', 'efficientnet_b0', etc.)
            pretrained: Whether to load pretrained weights
            
        Returns:
            Loaded model
            
        Raises:
            RuntimeError: If torch/torchvision not installed
            ValueError: If model not supported
        """
        self._check_availability()
        
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Model '{model_name}' not supported. "
                f"Supported models: {self.SUPPORTED_MODELS}"
            )
            
        # Return cached model if available
        if model_name in self._model_cache:
            return self._model_cache[model_name]
            
        # Load model
        try:
            if model_name == 'resnet50':
                if pretrained:
                    weights = self.torchvision.models.ResNet50_Weights.DEFAULT
                    model = self.torchvision.models.resnet50(weights=weights)
                else:
                    model = self.torchvision.models.resnet50()
            elif model_name == 'efficientnet_b0':
                if pretrained:
                    weights = self.torchvision.models.EfficientNet_B0_Weights.DEFAULT
                    model = self.torchvision.models.efficientnet_b0(weights=weights)
                else:
                    model = self.torchvision.models.efficientnet_b0()
            elif model_name == 'mobilenet_v2':
                if pretrained:
                    weights = self.torchvision.models.MobileNet_V2_Weights.DEFAULT
                    model = self.torchvision.models.mobilenet_v2(weights=weights)
                else:
                    model = self.torchvision.models.mobilenet_v2()
                    
            model = model.to(self.device)
            model.eval()
            
            self._model_cache[model_name] = model
            return model
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{model_name}': {e}")
            
    def predict(self, image_path: str, model_name: str) -> Dict[str, Any]:
        """
        Predict class for a single image
        
        Args:
            image_path: Path to image file
            model_name: Name of the model to use
            
        Returns:
            Dictionary with top-5 predictions and confidences
            
        Raises:
            RuntimeError: If torch/torchvision not installed
        """
        self._check_availability()
        
        model = self.load_model(model_name)
        preprocess = self._get_preprocess_transform()
        
        try:
            # Load and preprocess image
            image = self.Image.open(image_path).convert('RGB')
            input_tensor = preprocess(image).unsqueeze(0).to(self.device)
            
            # Run inference
            with self.torch.no_grad():
                output = model(input_tensor)
                
            # Get probabilities
            probabilities = self.torch.nn.functional.softmax(output[0], dim=0)
            
            # Get top-5 predictions
            top5_prob, top5_catid = self.torch.topk(probabilities, 5)
            
            predictions = []
            for i in range(5):
                predictions.append({
                    'class_id': int(top5_catid[i]),
                    'confidence': float(top5_prob[i])
                })
                
            return {
                'image_path': image_path,
                'model': model_name,
                'predictions': predictions,
                'device': self.device
            }
            
        except Exception as e:
            return {
                'image_path': image_path,
                'model': model_name,
                'error': str(e),
                'device': self.device
            }
            
    def batch_predict(self, image_paths: List[str], 
                     model_name: str) -> List[Dict[str, Any]]:
        """
        Predict classes for multiple images
        
        Args:
            image_paths: List of image file paths
            model_name: Name of the model to use
            
        Returns:
            List of dictionaries with predictions
            
        Raises:
            RuntimeError: If torch/torchvision not installed
        """
        self._check_availability()
        
        results = []
        for image_path in image_paths:
            result = self.predict(image_path, model_name)
            results.append(result)
            
        return results
        
    def extract_features(self, image_path: str, model_name: str) -> np.ndarray:
        """
        Extract features from penultimate layer
        
        Args:
            image_path: Path to image file
            model_name: Name of the model to use
            
        Returns:
            Feature vector as numpy array
            
        Raises:
            RuntimeError: If torch/torchvision not installed
        """
        self._check_availability()
        
        model = self.load_model(model_name)
        preprocess = self._get_preprocess_transform()
        
        try:
            # Load and preprocess image
            image = self.Image.open(image_path).convert('RGB')
            input_tensor = preprocess(image).unsqueeze(0).to(self.device)
            
            # Extract features from penultimate layer
            features = None
            
            def hook_fn(module, input, output):
                nonlocal features
                features = output
                
            # Register hook on appropriate layer
            if model_name == 'resnet50':
                handle = model.avgpool.register_forward_hook(hook_fn)
            elif model_name == 'efficientnet_b0':
                handle = model.avgpool.register_forward_hook(hook_fn)
            elif model_name == 'mobilenet_v2':
                handle = model.features[-1].register_forward_hook(hook_fn)
                
            # Run inference
            with self.torch.no_grad():
                _ = model(input_tensor)
                
            handle.remove()
            
            # Convert to numpy
            if features is not None:
                features_np = features.squeeze().cpu().numpy()
                return features_np
            else:
                raise RuntimeError("Failed to extract features")
                
        except Exception as e:
            raise RuntimeError(f"Failed to extract features: {e}")
            
    def is_available(self) -> bool:
        """
        Check if torch/torchvision is available
        
        Returns:
            True if available, False otherwise
        """
        return self.torch_available
        
    def get_device(self) -> str:
        """
        Get current device
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        return self.device
