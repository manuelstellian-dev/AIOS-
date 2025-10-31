"""
CUDA GPU Bridge for Hardware Access
Provides access to CUDA GPU information with graceful fallback
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CUDABridge:
    """
    CUDA GPU Bridge
    Access to GPU information (count, memory, compute capability)
    Gracefully falls back to simulated values if CUDA is unavailable
    """
    
    def __init__(self):
        self.available = False
        self.torch = None
        self._init_cuda()
    
    def _init_cuda(self):
        """Initialize CUDA connection"""
        try:
            import torch
            self.torch = torch
            if torch.cuda.is_available():
                self.available = True
                logger.info("CUDA bridge initialized successfully")
            else:
                logger.warning("CUDA not available - using simulated values")
        except ImportError:
            logger.warning("PyTorch not installed - using simulated values")
        except Exception as e:
            logger.error(f"CUDA initialization failed: {e}")
    
    def get_gpu_count(self) -> int:
        """
        Get number of available GPUs
        Returns 0 if CUDA is not available (simulated: returns 1)
        """
        if not self.available:
            logger.debug("CUDA not available - returning simulated GPU count")
            return 1  # Simulated value for testing
        
        try:
            return self.torch.cuda.device_count()
        except Exception as e:
            logger.error(f"Failed to get GPU count: {e}")
            return 0
    
    def get_gpu_info(self, device_id: int = 0) -> Dict[str, any]:
        """
        Get information about a specific GPU
        Returns dict with name, compute capability, total memory
        """
        if not self.available:
            return {
                "name": "Simulated GPU",
                "compute_capability": (7, 5),
                "total_memory_mb": 8192,
                "simulated": True
            }
        
        try:
            if device_id >= self.torch.cuda.device_count():
                logger.error(f"GPU {device_id} does not exist")
                return {}
            
            props = self.torch.cuda.get_device_properties(device_id)
            return {
                "name": props.name,
                "compute_capability": (props.major, props.minor),
                "total_memory_mb": props.total_memory // (1024 * 1024),
                "simulated": False
            }
        except Exception as e:
            logger.error(f"Failed to get GPU info: {e}")
            return {}
    
    def get_gpu_memory_usage(self, device_id: int = 0) -> Dict[str, float]:
        """
        Get GPU memory usage in MB
        Returns dict with allocated, reserved, free memory
        """
        if not self.available:
            return {
                "allocated_mb": 1024.0,
                "reserved_mb": 2048.0,
                "free_mb": 6144.0,
                "simulated": True
            }
        
        try:
            if device_id >= self.torch.cuda.device_count():
                logger.error(f"GPU {device_id} does not exist")
                return {}
            
            allocated = self.torch.cuda.memory_allocated(device_id) / (1024 * 1024)
            reserved = self.torch.cuda.memory_reserved(device_id) / (1024 * 1024)
            props = self.torch.cuda.get_device_properties(device_id)
            total = props.total_memory / (1024 * 1024)
            free = total - allocated
            
            return {
                "allocated_mb": allocated,
                "reserved_mb": reserved,
                "free_mb": free,
                "simulated": False
            }
        except Exception as e:
            logger.error(f"Failed to get GPU memory usage: {e}")
            return {}
    
    def is_tensor_core_available(self, device_id: int = 0) -> bool:
        """
        Check if GPU has Tensor Cores (compute capability >= 7.0)
        Returns True if available, False otherwise
        """
        if not self.available:
            logger.debug("CUDA not available - returning simulated Tensor Core availability")
            return True  # Simulated value
        
        try:
            if device_id >= self.torch.cuda.device_count():
                logger.error(f"GPU {device_id} does not exist")
                return False
            
            props = self.torch.cuda.get_device_properties(device_id)
            # Tensor cores are available on compute capability 7.0+
            return props.major >= 7
        except Exception as e:
            logger.error(f"Failed to check Tensor Core availability: {e}")
            return False
