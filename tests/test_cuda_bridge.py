"""Test CUDA Bridge"""
import pytest
from venom.hardware.cuda_bridge import CUDABridge

def test_cuda_bridge_init():
    """Test CUDA bridge initializes"""
    bridge = CUDABridge()
    assert bridge is not None

def test_cuda_bridge_get_gpu_count():
    """Test getting GPU count (graceful fallback)"""
    bridge = CUDABridge()
    count = bridge.get_gpu_count()
    
    # Should return either actual GPU count or simulated value (1)
    assert isinstance(count, int)
    assert count >= 0
    
    # If CUDA not available, should return simulated value
    if not bridge.available:
        assert count == 1

def test_cuda_bridge_get_gpu_info():
    """Test getting GPU info"""
    bridge = CUDABridge()
    info = bridge.get_gpu_info(0)
    
    assert isinstance(info, dict)
    assert "name" in info
    assert "compute_capability" in info
    assert "total_memory_mb" in info
    assert "simulated" in info
    
    # Check compute capability format
    assert isinstance(info["compute_capability"], tuple)
    assert len(info["compute_capability"]) == 2

def test_cuda_bridge_get_gpu_memory_usage():
    """Test getting GPU memory usage"""
    bridge = CUDABridge()
    memory = bridge.get_gpu_memory_usage(0)
    
    assert isinstance(memory, dict)
    assert "allocated_mb" in memory
    assert "reserved_mb" in memory
    assert "free_mb" in memory
    assert "simulated" in memory
    
    # All memory values should be non-negative
    assert memory["allocated_mb"] >= 0
    assert memory["reserved_mb"] >= 0
    assert memory["free_mb"] >= 0

def test_cuda_bridge_is_tensor_core_available():
    """Test Tensor Core availability check"""
    bridge = CUDABridge()
    has_tensor_cores = bridge.is_tensor_core_available(0)
    
    assert isinstance(has_tensor_cores, bool)
    
    # If CUDA not available, should return simulated value (True)
    if not bridge.available:
        assert has_tensor_cores == True
