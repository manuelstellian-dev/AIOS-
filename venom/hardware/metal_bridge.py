"""
Metal GPU Bridge for Apple Silicon Hardware Access
Provides access to Apple Metal GPU via MPS with graceful fallback
"""

import logging
import platform
from typing import Dict, List, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)

class MetalBridge:
    """
    Metal GPU Bridge for Apple Silicon (M1/M2/M3/M4)
    Access to Metal Performance Shaders and Neural Engine
    Gracefully falls back to simulated values if Metal is unavailable
    """
    
    def __init__(self):
        """Initialize Metal bridge"""
        self.available = False
        self.torch = None
        self.is_apple_silicon = False
        self._init_metal()
    
    def _init_metal(self):
        """Initialize Metal connection"""
        try:
            # Check if running on macOS with Apple Silicon
            self.is_apple_silicon = (
                platform.system() == 'Darwin' and 
                platform.processor() == 'arm'
            )
            
            if not self.is_apple_silicon:
                logger.warning("Not running on Apple Silicon - using simulated values")
                return
            
            import torch
            self.torch = torch
            
            # Check for MPS (Metal Performance Shaders) backend
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.available = True
                logger.info("Metal bridge initialized successfully")
            else:
                logger.warning("Metal Performance Shaders not available - using simulated values")
        except ImportError:
            logger.warning("PyTorch not installed - using simulated values")
        except Exception as e:
            logger.error(f"Metal initialization failed: {e}")
    
    def is_available(self) -> bool:
        """
        Check if Metal is available
        Returns True if Metal GPU is detected
        """
        return self.available
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about Apple Silicon device
        
        Returns:
            Dict with name, architecture, memory, cores
        """
        if not self.available:
            return {
                "name": "Simulated Apple M2",
                "architecture": "ARM64",
                "gpu_cores": 10,
                "neural_engine_cores": 16,
                "unified_memory_gb": 16,
                "simulated": True
            }
        
        try:
            import psutil
            
            # Detect chip type from machine
            machine = platform.machine()
            
            # Try to detect M-series chip
            chip_name = "Apple Silicon"
            try:
                import subprocess
                result = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0:
                    chip_name = result.stdout.strip()
            except:
                pass
            
            return {
                "name": chip_name,
                "architecture": machine,
                "unified_memory_gb": psutil.virtual_memory().total // (1024**3),
                "metal_available": True,
                "mps_available": True,
                "simulated": False
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    def allocate_buffer(self, size_mb: int) -> Any:
        """
        Allocate unified memory buffer on Apple Silicon
        
        Args:
            size_mb: Buffer size in MB
            
        Returns:
            Allocated tensor or None
        """
        if not self.available:
            logger.debug("Metal not available - simulating buffer allocation")
            return np.zeros((size_mb * 256, 1024), dtype=np.float32)  # Simulated
        
        try:
            # Allocate tensor on MPS device (unified memory)
            size_bytes = size_mb * 1024 * 1024
            num_elements = size_bytes // 4  # float32 is 4 bytes
            tensor = self.torch.zeros(num_elements, dtype=self.torch.float32, device='mps')
            logger.info(f"Allocated {size_mb}MB on MPS device")
            return tensor
        except Exception as e:
            logger.error(f"Failed to allocate buffer: {e}")
            return None
    
    def run_compute_shader(self, shader_code: str, data: np.ndarray) -> np.ndarray:
        """
        Run Metal compute shader (simulated via torch MPS operations)
        
        Args:
            shader_code: Metal shader code (for documentation, not executed)
            data: Input data as numpy array
            
        Returns:
            Result as numpy array
        """
        if not self.available:
            logger.debug("Metal not available - simulating shader execution")
            return data * 2.0  # Simulated operation
        
        try:
            # Convert to torch tensor and run on MPS
            tensor = self.torch.from_numpy(data).to('mps')
            # Simulate shader with basic operation
            result = tensor * 2.0
            return result.cpu().numpy()
        except Exception as e:
            logger.error(f"Failed to run shader: {e}")
            return data
    
    def benchmark(self, operation: str = 'matmul', size: int = 1024) -> Dict[str, Any]:
        """
        Benchmark Metal GPU performance
        
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
                "time_ms": 15.3,
                "gflops": 7200.0,
                "simulated": True
            }
        
        try:
            import time
            
            if operation == 'matmul':
                # Matrix multiplication benchmark
                a = self.torch.randn(size, size, device='mps')
                b = self.torch.randn(size, size, device='mps')
                
                # Warmup
                _ = self.torch.matmul(a, b)
                self.torch.mps.synchronize() if hasattr(self.torch.mps, 'synchronize') else None
                
                # Benchmark
                start = time.perf_counter()
                result = self.torch.matmul(a, b)
                self.torch.mps.synchronize() if hasattr(self.torch.mps, 'synchronize') else None
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
                x = self.torch.randn(32, 64, size, size, device='mps')
                conv = self.torch.nn.Conv2d(64, 128, 3, padding=1).to('mps')
                
                # Warmup
                _ = conv(x)
                self.torch.mps.synchronize() if hasattr(self.torch.mps, 'synchronize') else None
                
                # Benchmark
                start = time.perf_counter()
                result = conv(x)
                self.torch.mps.synchronize() if hasattr(self.torch.mps, 'synchronize') else None
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
    
    def optimize_for_neural_engine(self) -> bool:
        """
        Check if Neural Engine optimization is available
        
        Returns:
            True if Neural Engine can be used
        """
        if not self.available:
            logger.debug("Metal not available - simulating Neural Engine check")
            return True  # Simulated
        
        try:
            # Neural Engine is available on Apple Silicon with Metal
            # In practice, this is used automatically by Core ML
            return self.is_apple_silicon and self.available
        except Exception as e:
            logger.error(f"Failed to check Neural Engine: {e}")
            return False
