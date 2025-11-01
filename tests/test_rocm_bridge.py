"""Test ROCm Bridge"""
import pytest
from venom.hardware.rocm_bridge import ROCmBridge
import numpy as np


def test_rocm_detection():
    """Test ROCm bridge initializes and detects availability"""
    bridge = ROCmBridge()
    assert bridge is not None
    assert isinstance(bridge.is_available(), bool)


def test_device_count():
    """Test getting ROCm device count (graceful fallback)"""
    bridge = ROCmBridge()
    count = bridge.get_device_count()
    
    # Should return either actual GPU count or simulated value (1)
    assert isinstance(count, int)
    assert count >= 0
    
    # If ROCm not available, should return simulated value
    if not bridge.available:
        assert count == 1


def test_device_info():
    """Test getting ROCm device info"""
    bridge = ROCmBridge()
    info = bridge.get_device_info(0)
    
    assert isinstance(info, dict)
    assert "name" in info
    assert "compute_capability" in info
    assert "total_memory_mb" in info
    assert "architecture" in info
    assert "simulated" in info
    
    # Check memory is positive
    assert info["total_memory_mb"] > 0


def test_memory_allocation():
    """Test ROCm memory allocation"""
    bridge = ROCmBridge()
    size_mb = 10
    
    # Should allocate or simulate allocation
    buffer = bridge.allocate_memory(size_mb, 0)
    assert buffer is not None
    
    # If simulated, should be numpy array
    if not bridge.available:
        assert isinstance(buffer, np.ndarray)


def test_benchmark():
    """Test ROCm benchmarking"""
    bridge = ROCmBridge()
    
    # Test matrix multiplication benchmark
    result = bridge.benchmark(operation='matmul', size=512)
    assert isinstance(result, dict)
    assert "operation" in result
    assert "size" in result
    assert "time_ms" in result
    assert "simulated" in result
    
    # Time should be positive
    assert result["time_ms"] > 0
    
    # Test convolution benchmark
    result_conv = bridge.benchmark(operation='convolution', size=64)
    assert isinstance(result_conv, dict)
    assert "operation" in result_conv
    assert result_conv["operation"] == "convolution"
