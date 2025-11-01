"""
Universal Hardware Scanner - Cross-platform hardware detection for VENOM Ω-AIOS

Detects CPU, Memory, GPU, Thermal across ANY device:
- Raspberry Pi
- Laptops (Windows/macOS/Linux)
- Cloud instances (AWS, Azure, GCP)

Auto-calculates Möbius parameters:
- N: optimal workers
- Λ: lambda_wrap [10-832]
- P: parallel_fraction [0.60-0.95]
"""

import platform
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    """Complete hardware profile for adaptive execution"""
    # CPU
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_arch: str
    cpu_vendor: str
    cpu_freq_current: float
    cpu_freq_max: float
    cpu_usage_percent: float
    
    # Memory
    memory_total_gb: float
    memory_available_gb: float
    memory_usage_percent: float
    swap_total_gb: float
    
    # GPU
    has_cuda: bool
    has_rocm: bool
    has_metal: bool
    has_opencl: bool
    gpu_info: Optional[Dict[str, Any]] = None
    
    # Thermal
    cpu_temperature: Optional[float] = None
    
    # Platform
    platform_system: str = ""
    platform_version: str = ""
    platform_machine: str = ""
    
    # Capabilities
    has_hyperthreading: bool = False
    has_virtualization: bool = False
    is_docker: bool = False
    is_kubernetes: bool = False
    
    # Calculated Möbius Parameters
    optimal_workers: int = 4
    lambda_wrap: float = 200.0
    parallel_fraction: float = 0.75


class UniversalHardwareScanner:
    """
    Cross-platform hardware scanner with adaptive Möbius parameter calculation
    
    Detects hardware capabilities and auto-configures:
    - N (optimal_workers): Based on cores, memory, GPU
    - Λ (lambda_wrap): Based on compute capacity [10-832]
    - P (parallel_fraction): Based on parallelization capability [0.60-0.95]
    """
    
    LAMBDA_WRAP_MIN = 10.0
    LAMBDA_WRAP_MAX = 832.0
    
    def __init__(self):
        if psutil is None:
            raise ImportError(
                "psutil is required for UniversalHardwareScanner. "
                "Install with: pip install psutil>=5.9.0"
            )
        self.profile: Optional[HardwareProfile] = None
        
    def scan(self) -> HardwareProfile:
        """
        Perform full hardware scan and calculate Möbius parameters
        
        Returns:
            HardwareProfile with all detected capabilities
        """
        logger.info("🔍 Starting universal hardware scan...")
        
        cpu_info = self._scan_cpu()
        memory_info = self._scan_memory()
        gpu_info = self._scan_gpu()
        thermal_info = self._scan_thermal()
        platform_info = self._scan_platform()
        capabilities = self._scan_capabilities()
        
        # Create base profile
        self.profile = HardwareProfile(
            # CPU
            cpu_cores_physical=cpu_info['physical'],
            cpu_cores_logical=cpu_info['logical'],
            cpu_arch=cpu_info['arch'],
            cpu_vendor=cpu_info['vendor'],
            cpu_freq_current=cpu_info['freq_current'],
            cpu_freq_max=cpu_info['freq_max'],
            cpu_usage_percent=cpu_info['usage'],
            
            # Memory
            memory_total_gb=memory_info['total_gb'],
            memory_available_gb=memory_info['available_gb'],
            memory_usage_percent=memory_info['usage_percent'],
            swap_total_gb=memory_info['swap_gb'],
            
            # GPU
            has_cuda=gpu_info['cuda'],
            has_rocm=gpu_info['rocm'],
            has_metal=gpu_info['metal'],
            has_opencl=gpu_info['opencl'],
            gpu_info=gpu_info.get('info'),
            
            # Thermal
            cpu_temperature=thermal_info.get('temperature'),
            
            # Platform
            platform_system=platform_info['system'],
            platform_version=platform_info['version'],
            platform_machine=platform_info['machine'],
            
            # Capabilities
            has_hyperthreading=capabilities['hyperthreading'],
            has_virtualization=capabilities['virtualization'],
            is_docker=capabilities['docker'],
            is_kubernetes=capabilities['kubernetes'],
        )
        
        # Calculate Möbius parameters
        self.profile.optimal_workers = self.get_optimal_workers()
        self.profile.lambda_wrap = self.get_adaptive_lambda()
        self.profile.parallel_fraction = self.get_parallel_fraction()
        
        logger.info(f"✅ Hardware scan complete: {self.profile.cpu_cores_logical} cores, "
                   f"{self.profile.memory_total_gb:.1f}GB RAM")
        logger.info(f"📐 Möbius Parameters: N={self.profile.optimal_workers}, "
                   f"Λ={self.profile.lambda_wrap:.1f}, P={self.profile.parallel_fraction:.3f}")
        
        return self.profile
    
    def _scan_cpu(self) -> Dict[str, Any]:
        """Scan CPU information"""
        try:
            physical = psutil.cpu_count(logical=False) or 1
            logical = psutil.cpu_count(logical=True) or 1
            
            # Get CPU frequency
            freq = psutil.cpu_freq()
            freq_current = freq.current if freq else 0.0
            freq_max = freq.max if freq and freq.max else freq_current
            
            # Get current usage
            usage = psutil.cpu_percent(interval=0.1)
            
            # Platform-specific info
            arch = platform.machine()
            vendor = self._get_cpu_vendor()
            
            return {
                'physical': physical,
                'logical': logical,
                'arch': arch,
                'vendor': vendor,
                'freq_current': freq_current,
                'freq_max': freq_max,
                'usage': usage
            }
        except Exception as e:
            logger.warning(f"Error scanning CPU: {e}")
            return {
                'physical': 1, 'logical': 1, 'arch': 'unknown',
                'vendor': 'unknown', 'freq_current': 0.0,
                'freq_max': 0.0, 'usage': 0.0
            }
    
    def _get_cpu_vendor(self) -> str:
        """Detect CPU vendor"""
        machine = platform.machine().lower()
        system = platform.system().lower()
        
        if 'arm' in machine or 'aarch64' in machine:
            return 'ARM'
        elif 'x86' in machine or 'amd64' in machine or 'i386' in machine or 'i686' in machine:
            # Could be Intel or AMD
            try:
                if system == 'linux':
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read().lower()
                        if 'amd' in cpuinfo:
                            return 'AMD'
                        elif 'intel' in cpuinfo:
                            return 'Intel'
            except:
                pass
            return 'x86'
        else:
            return 'unknown'
    
    def _scan_memory(self) -> Dict[str, Any]:
        """Scan memory information"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total_gb': mem.total / (1024**3),
                'available_gb': mem.available / (1024**3),
                'usage_percent': mem.percent,
                'swap_gb': swap.total / (1024**3)
            }
        except Exception as e:
            logger.warning(f"Error scanning memory: {e}")
            return {
                'total_gb': 0.0, 'available_gb': 0.0,
                'usage_percent': 0.0, 'swap_gb': 0.0
            }
    
    def _scan_gpu(self) -> Dict[str, Any]:
        """Scan GPU capabilities"""
        gpu_info = {
            'cuda': self._check_cuda(),
            'rocm': self._check_rocm(),
            'metal': self._check_metal(),
            'opencl': self._check_opencl(),
            'info': None
        }
        
        # Get detailed GPU info if CUDA is available
        if gpu_info['cuda']:
            gpu_info['info'] = self._get_cuda_info()
        
        return gpu_info
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _check_rocm(self) -> bool:
        """Check if ROCm is available"""
        try:
            import torch
            return hasattr(torch, 'hip') and torch.hip.is_available()
        except:
            return False
    
    def _check_metal(self) -> bool:
        """Check if Metal is available (macOS)"""
        try:
            import torch
            return hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        except:
            return False
    
    def _check_opencl(self) -> bool:
        """Check if OpenCL is available"""
        try:
            import pyopencl
            platforms = pyopencl.get_platforms()
            return len(platforms) > 0
        except:
            return False
    
    def _get_cuda_info(self) -> Optional[Dict[str, Any]]:
        """Get detailed CUDA GPU information"""
        try:
            import torch
            if not torch.cuda.is_available():
                return None
            
            device_count = torch.cuda.device_count()
            devices = []
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                devices.append({
                    'name': props.name,
                    'compute_capability': f"{props.major}.{props.minor}",
                    'memory_gb': props.total_memory / (1024**3)
                })
            
            return {
                'device_count': device_count,
                'devices': devices
            }
        except Exception as e:
            logger.warning(f"Error getting CUDA info: {e}")
            return None
    
    def _scan_thermal(self) -> Dict[str, Optional[float]]:
        """Scan thermal information"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to get CPU temperature
                for name, entries in temps.items():
                    if 'coretemp' in name.lower() or 'cpu' in name.lower():
                        if entries:
                            # Return average temperature
                            avg_temp = sum(e.current for e in entries) / len(entries)
                            return {'temperature': avg_temp}
                
                # Fallback: return first available temperature
                for name, entries in temps.items():
                    if entries:
                        avg_temp = sum(e.current for e in entries) / len(entries)
                        return {'temperature': avg_temp}
        except:
            pass
        
        return {'temperature': None}
    
    def _scan_platform(self) -> Dict[str, str]:
        """Scan platform information"""
        return {
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine()
        }
    
    def _scan_capabilities(self) -> Dict[str, bool]:
        """Scan system capabilities"""
        capabilities = {
            'hyperthreading': False,
            'virtualization': False,
            'docker': False,
            'kubernetes': False
        }
        
        # Check hyperthreading
        try:
            physical = psutil.cpu_count(logical=False) or 1
            logical = psutil.cpu_count(logical=True) or 1
            capabilities['hyperthreading'] = logical > physical
        except:
            pass
        
        # Check Docker
        try:
            import os
            capabilities['docker'] = os.path.exists('/.dockerenv')
        except:
            pass
        
        # Check Kubernetes
        try:
            import os
            capabilities['kubernetes'] = (
                os.environ.get('KUBERNETES_SERVICE_HOST') is not None
            )
        except:
            pass
        
        return capabilities
    
    def get_optimal_workers(self) -> int:
        """
        Calculate optimal number of workers (N) based on hardware
        
        Logic:
        - Start with logical cores
        - Reduce if low memory (<8GB)
        - Boost if GPU available
        - Clamp to reasonable range [1, 64]
        
        Returns:
            Optimal worker count
        """
        if not self.profile:
            return 4  # Default fallback
        
        # Start with logical cores
        workers = self.profile.cpu_cores_logical
        
        # Adjust for memory constraints
        if self.profile.memory_total_gb < 4:
            workers = max(1, workers // 2)
        elif self.profile.memory_total_gb < 8:
            workers = max(2, int(workers * 0.75))
        
        # Boost for GPU
        if self.profile.has_cuda or self.profile.has_rocm or self.profile.has_metal:
            workers = int(workers * 1.5)
        
        # Clamp to reasonable range
        workers = max(1, min(64, workers))
        
        return workers
    
    def get_adaptive_lambda(self) -> float:
        """
        Calculate adaptive lambda_wrap (Λ) based on compute capacity
        
        Formula: cores × 50, scaled by RAM
        Range: [10, 832]
        
        Returns:
            Lambda wrap value
        """
        if not self.profile:
            return 200.0  # Default fallback
        
        # Base calculation: cores × 50
        base_lambda = self.profile.cpu_cores_logical * 50.0
        
        # Scale by memory
        memory_factor = 1.0
        if self.profile.memory_total_gb < 4:
            memory_factor = 0.5
        elif self.profile.memory_total_gb < 8:
            memory_factor = 0.75
        elif self.profile.memory_total_gb >= 16:
            memory_factor = 1.5
        elif self.profile.memory_total_gb >= 32:
            memory_factor = 2.0
        
        # GPU boost
        gpu_factor = 1.0
        if self.profile.has_cuda or self.profile.has_rocm or self.profile.has_metal:
            gpu_factor = 1.5
        
        # Calculate final lambda
        lambda_wrap = base_lambda * memory_factor * gpu_factor
        
        # Clamp to range
        lambda_wrap = max(self.LAMBDA_WRAP_MIN, min(self.LAMBDA_WRAP_MAX, lambda_wrap))
        
        return lambda_wrap
    
    def get_parallel_fraction(self) -> float:
        """
        Calculate parallel fraction (P) based on parallelization capability
        
        Logic:
        - More cores → higher P
        - Range: [0.60, 0.95]
        
        Returns:
            Parallel fraction
        """
        if not self.profile:
            return 0.75  # Default fallback
        
        cores = self.profile.cpu_cores_logical
        
        # Map cores to parallel fraction
        if cores <= 2:
            p = 0.60
        elif cores <= 4:
            p = 0.70
        elif cores <= 8:
            p = 0.80
        elif cores <= 16:
            p = 0.85
        elif cores <= 32:
            p = 0.90
        else:
            p = 0.95
        
        return p
    
    def print_profile(self):
        """Print human-readable hardware profile"""
        if not self.profile:
            print("❌ No hardware profile available. Run scan() first.")
            return
        
        print("\n" + "="*60)
        print("🌌 VENOM Ω-AIOS Universal Hardware Profile")
        print("="*60)
        
        print(f"\n💻 CPU:")
        print(f"  Cores: {self.profile.cpu_cores_physical} physical, "
              f"{self.profile.cpu_cores_logical} logical")
        print(f"  Architecture: {self.profile.cpu_arch}")
        print(f"  Vendor: {self.profile.cpu_vendor}")
        print(f"  Frequency: {self.profile.cpu_freq_current:.0f} MHz "
              f"(max: {self.profile.cpu_freq_max:.0f} MHz)")
        print(f"  Usage: {self.profile.cpu_usage_percent:.1f}%")
        
        print(f"\n🧠 Memory:")
        print(f"  Total: {self.profile.memory_total_gb:.2f} GB")
        print(f"  Available: {self.profile.memory_available_gb:.2f} GB")
        print(f"  Usage: {self.profile.memory_usage_percent:.1f}%")
        print(f"  Swap: {self.profile.swap_total_gb:.2f} GB")
        
        print(f"\n🎮 GPU:")
        gpu_available = []
        if self.profile.has_cuda:
            gpu_available.append("CUDA")
        if self.profile.has_rocm:
            gpu_available.append("ROCm")
        if self.profile.has_metal:
            gpu_available.append("Metal")
        if self.profile.has_opencl:
            gpu_available.append("OpenCL")
        
        if gpu_available:
            print(f"  Available: {', '.join(gpu_available)}")
            if self.profile.gpu_info:
                print(f"  Devices: {self.profile.gpu_info.get('device_count', 0)}")
        else:
            print(f"  Available: None")
        
        if self.profile.cpu_temperature:
            print(f"\n🌡️  CPU Temperature: {self.profile.cpu_temperature:.1f}°C")
        
        print(f"\n🖥️  Platform:")
        print(f"  System: {self.profile.platform_system}")
        print(f"  Machine: {self.profile.platform_machine}")
        
        print(f"\n⚙️  Capabilities:")
        print(f"  Hyperthreading: {'✅' if self.profile.has_hyperthreading else '❌'}")
        print(f"  Virtualization: {'✅' if self.profile.has_virtualization else '❌'}")
        print(f"  Docker: {'✅' if self.profile.is_docker else '❌'}")
        print(f"  Kubernetes: {'✅' if self.profile.is_kubernetes else '❌'}")
        
        print(f"\n📐 Möbius Parameters:")
        print(f"  N (workers): {self.profile.optimal_workers}")
        print(f"  Λ (lambda_wrap): {self.profile.lambda_wrap:.1f}")
        print(f"  P (parallel_fraction): {self.profile.parallel_fraction:.3f}")
        
        print("="*60 + "\n")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export profile as dictionary"""
        if not self.profile:
            return {}
        return asdict(self.profile)


# Convenience function
def scan_hardware() -> HardwareProfile:
    """Quick scan function"""
    scanner = UniversalHardwareScanner()
    return scanner.scan()


if __name__ == "__main__":
    # Demo
    scanner = UniversalHardwareScanner()
    profile = scanner.scan()
    scanner.print_profile()
