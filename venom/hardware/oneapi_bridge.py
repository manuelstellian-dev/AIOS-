"""
oneAPI Bridge for Intel XPU Hardware Access
Provides access to Intel integrated/discrete GPUs via oneAPI/SYCL
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)

class OneAPIBridge:
    """
    oneAPI Bridge for Intel XPU (integrated/discrete GPUs)
    Access to Intel GPU information via SYCL
    Gracefully falls back to simulated values if oneAPI is unavailable
    """
    
    def __init__(self):
        """Initialize oneAPI bridge"""
        self.available = False
        self.torch = None
        self._init_oneapi()
    
    def _init_oneapi(self):
        """Initialize oneAPI connection"""
        try:
            import torch
            self.torch = torch
            
            # Check for Intel XPU backend (torch-xpu)
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                self.available = True
                logger.info("oneAPI bridge initialized successfully")
            else:
                logger.warning("Intel XPU not available - using simulated values")
        except ImportError:
            logger.warning("PyTorch not installed - using simulated values")
        except Exception as e:
            logger.error(f"oneAPI initialization failed: {e}")
    
    def is_available(self) -> bool:
        """
        Check if Intel XPU is available
        Returns True if Intel GPU is detected
        """
        return self.available
    
    def get_device_count(self) -> int:
        """
        Get number of available Intel XPUs
        Returns simulated value (1) if oneAPI is not available
        """
        if not self.available:
            logger.debug("oneAPI not available - returning simulated device count")
            return 1  # Simulated value for testing
        
        try:
            return self.torch.xpu.device_count()
        except Exception as e:
            logger.error(f"Failed to get device count: {e}")
            return 0
    
    def get_device_info(self, device_id: int = 0) -> Dict[str, Any]:
        """
        Get information about a specific Intel XPU
        
        Args:
            device_id: XPU device ID (default: 0)
            
        Returns:
            Dict with name, driver version, memory, compute units
        """
        if not self.available:
            return {
                "name": "Simulated Intel Arc A770",
                "type": "discrete",
                "driver_version": "1.3.0",
                "total_memory_mb": 16384,
                "compute_units": 512,
                "simulated": True
            }
        
        try:
            if device_id >= self.torch.xpu.device_count():
                logger.error(f"XPU {device_id} does not exist")
                return {}
            
            props = self.torch.xpu.get_device_properties(device_id)
            return {
                "name": props.name if hasattr(props, 'name') else "Intel XPU",
                "type": props.type if hasattr(props, 'type') else "unknown",
                "total_memory_mb": props.total_memory // (1024 * 1024) if hasattr(props, 'total_memory') else 0,
                "driver_version": props.driver_version if hasattr(props, 'driver_version') else "unknown",
                "simulated": False
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    def run_sycl_kernel(self, kernel_code: str, data: np.ndarray) -> np.ndarray:
        """
        Run SYCL kernel on Intel XPU (simulated via torch operations)
        
        Args:
            kernel_code: SYCL kernel code (for documentation, not executed)
            data: Input data as numpy array
            
        Returns:
            Result as numpy array
        """
        if not self.available:
            logger.debug("oneAPI not available - simulating kernel execution")
            return data * 2.0  # Simulated operation
        
        try:
            # Convert to torch tensor and run on XPU
            tensor = self.torch.from_numpy(data).to('xpu:0')
            # Simulate kernel with basic operation
            result = tensor * 2.0
            return result.cpu().numpy()
        except Exception as e:
            logger.error(f"Failed to run kernel: {e}")
            return data
    
    def benchmark(self, operation: str = 'matmul', size: int = 1024) -> Dict[str, Any]:
        """
        Benchmark Intel XPU performance
        
        Args:
            operation: Operation to benchmark ('matmul', 'convolution')
            size: Problem size (default: 1024)
            
        Returns:
            Dict with benchmark results (time_ms, gflops, etc.)
        """
        if not self.available:
            return {
                "operation": operation,
                "size": size,
                "time_ms": 18.7,
                "gflops": 5800.0,
                "simulated": True
            }
        
        try:
            import time
            
            if operation == 'matmul':
                # Matrix multiplication benchmark
                a = self.torch.randn(size, size, device='xpu:0')
                b = self.torch.randn(size, size, device='xpu:0')
                
                # Warmup
                _ = self.torch.matmul(a, b)
                self.torch.xpu.synchronize()
                
                # Benchmark
                start = time.perf_counter()
                result = self.torch.matmul(a, b)
                self.torch.xpu.synchronize()
                elapsed = (time.perf_counter() - start) * 1000
                
                # Calculate GFLOPS (2*N^3 operations for matmul)
                ops = 2 * size * size * size
                gflops = (ops / 1e9) / (elapsed / 1000)
                
                return {
                    "operation": operation,
                    "size": size,
                    "time_ms": elapsed,
                    "gflops": gflops,
                    "simulated": False
                }
            
            elif operation == 'convolution':
                # Convolution benchmark
                x = self.torch.randn(32, 64, size, size, device='xpu:0')
                conv = self.torch.nn.Conv2d(64, 128, 3, padding=1).to('xpu:0')
                
                # Warmup
                _ = conv(x)
                self.torch.xpu.synchronize()
                
                # Benchmark
                start = time.perf_counter()
                result = conv(x)
                self.torch.xpu.synchronize()
                elapsed = (time.perf_counter() - start) * 1000
                
                return {
                    "operation": operation,
                    "size": size,
                    "time_ms": elapsed,
                    "simulated": False
                }
            
            else:
                return {
                    "operation": operation,
                    "error": "Unsupported operation",
                    "simulated": False
                }
                
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {
                "operation": operation,
                "size": size,
                "error": str(e),
                "simulated": False
            }
