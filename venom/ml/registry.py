"""
Model Registry - Version tracking and registry for ML models
Stores model metadata, tracks versions, and manages performance metrics
"""
import os
import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from pathlib import Path


class ModelRegistry:
    """
    Model registry for version tracking and performance monitoring
    Stores model metadata in JSON index file with SHA256 checksums
    """
    
    def __init__(self, storage_path: str = './models/registry'):
        """
        Initialize model registry
        
        Args:
            storage_path: Path to store registry index and metadata
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_path / 'registry_index.json'
        self.index = self._load_index()
        
    def _load_index(self) -> Dict[str, Any]:
        """
        Load registry index from disk
        
        Returns:
            Dictionary containing registry index
        """
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {'models': {}, 'metadata': {'created': time.time()}}
        
    def _save_index(self):
        """Save registry index to disk"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
            
    def _calculate_checksum(self, model_path: str) -> str:
        """
        Calculate SHA256 checksum of model file
        
        Args:
            model_path: Path to model file
            
        Returns:
            SHA256 checksum as hex string
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(model_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            # If file doesn't exist, return hash of path
            return hashlib.sha256(model_path.encode()).hexdigest()
            
    def register_model(self, name: str, version: str, metadata: Dict[str, Any], 
                      model_path: str) -> Dict[str, Any]:
        """
        Register a new model version
        
        Args:
            name: Model name
            version: Model version string
            metadata: Additional metadata (architecture, framework, etc.)
            model_path: Path to model file
            
        Returns:
            Dictionary with registration details
        """
        if name not in self.index['models']:
            self.index['models'][name] = {'versions': {}}
            
        checksum = self._calculate_checksum(model_path)
        
        version_data = {
            'version': version,
            'metadata': metadata,
            'model_path': model_path,
            'checksum': checksum,
            'registered_at': time.time(),
            'performance_metrics': {}
        }
        
        self.index['models'][name]['versions'][version] = version_data
        self._save_index()
        
        return {
            'name': name,
            'version': version,
            'checksum': checksum,
            'registered_at': version_data['registered_at']
        }
        
    def get_model(self, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get model information
        
        Args:
            name: Model name
            version: Model version (None returns latest)
            
        Returns:
            Dictionary with model information
            
        Raises:
            KeyError: If model or version not found
        """
        if name not in self.index['models']:
            raise KeyError(f"Model '{name}' not found in registry")
            
        model_data = self.index['models'][name]
        
        if version is None:
            # Return latest version (most recent timestamp)
            versions = model_data['versions']
            if not versions:
                raise KeyError(f"No versions found for model '{name}'")
            latest = max(versions.items(), 
                        key=lambda x: x[1]['registered_at'])
            version = latest[0]
            
        if version not in model_data['versions']:
            raise KeyError(f"Version '{version}' not found for model '{name}'")
            
        return {
            'name': name,
            'version': version,
            **model_data['versions'][version]
        }
        
    def list_models(self) -> List[str]:
        """
        List all registered model names
        
        Returns:
            List of model names
        """
        return list(self.index['models'].keys())
        
    def list_versions(self, name: str) -> List[str]:
        """
        List all versions of a model
        
        Args:
            name: Model name
            
        Returns:
            List of version strings
            
        Raises:
            KeyError: If model not found
        """
        if name not in self.index['models']:
            raise KeyError(f"Model '{name}' not found in registry")
            
        return list(self.index['models'][name]['versions'].keys())
        
    def track_performance(self, name: str, version: str, metrics: Dict[str, float]):
        """
        Track performance metrics for a model version
        
        Args:
            name: Model name
            version: Model version
            metrics: Dictionary of metric names to values
            
        Raises:
            KeyError: If model or version not found
        """
        if name not in self.index['models']:
            raise KeyError(f"Model '{name}' not found in registry")
            
        if version not in self.index['models'][name]['versions']:
            raise KeyError(f"Version '{version}' not found for model '{name}'")
            
        version_data = self.index['models'][name]['versions'][version]
        version_data['performance_metrics'].update(metrics)
        version_data['last_metric_update'] = time.time()
        self._save_index()
        
    def get_best_model(self, name: str, metric: str = 'accuracy') -> Dict[str, Any]:
        """
        Get best performing model version based on metric
        
        Args:
            name: Model name
            metric: Metric name to optimize (default: 'accuracy')
            
        Returns:
            Dictionary with best model information
            
        Raises:
            KeyError: If model not found
            ValueError: If no versions have the specified metric
        """
        if name not in self.index['models']:
            raise KeyError(f"Model '{name}' not found in registry")
            
        versions = self.index['models'][name]['versions']
        
        # Filter versions that have the metric
        versions_with_metric = {
            v: data for v, data in versions.items()
            if metric in data.get('performance_metrics', {})
        }
        
        if not versions_with_metric:
            raise ValueError(
                f"No versions of model '{name}' have metric '{metric}'"
            )
            
        # Find version with best (highest) metric value
        best_version = max(
            versions_with_metric.items(),
            key=lambda x: x[1]['performance_metrics'][metric]
        )
        
        return {
            'name': name,
            'version': best_version[0],
            **best_version[1]
        }
        
    def delete_model(self, name: str, version: str):
        """
        Delete a model version from registry
        
        Args:
            name: Model name
            version: Model version
            
        Raises:
            KeyError: If model or version not found
        """
        if name not in self.index['models']:
            raise KeyError(f"Model '{name}' not found in registry")
            
        if version not in self.index['models'][name]['versions']:
            raise KeyError(f"Version '{version}' not found for model '{name}'")
            
        del self.index['models'][name]['versions'][version]
        
        # Remove model entry if no versions left
        if not self.index['models'][name]['versions']:
            del self.index['models'][name]
            
        self._save_index()
