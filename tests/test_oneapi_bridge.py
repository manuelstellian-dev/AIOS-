"""Test oneAPI Bridge"""
import pytest
from venom.hardware.oneapi_bridge import OneAPIBridge
import numpy as np


def test_oneapi_detection():
    """Test oneAPI bridge initializes and detects availability"""
    bridge = OneAPIBridge()
    assert bridge is not None
    assert isinstance(bridge.is_available(), bool)


def test_device_count():
    """Test getting oneAPI device count (graceful fallback)"""
    bridge = OneAPIBridge()
    count = bridge.get_device_count()
    
    # Should return either actual XPU count or simulated value (1)
    assert isinstance(count, int)
    assert count >= 0
    
    # If oneAPI not available, should return simulated value
    if not bridge.available:
        assert count == 1


def test_device_info():
    """Test getting oneAPI device info"""
    bridge = OneAPIBridge()
    info = bridge.get_device_info(0)
    
    assert isinstance(info, dict)
    assert "name" in info
    assert "type" in info
    assert "total_memory_mb" in info
    assert "simulated" in info
    
    # Memory should be positive
    assert info["total_memory_mb"] > 0


def test_sycl_kernel():
    """Test SYCL kernel execution (simulated)"""
    bridge = OneAPIBridge()
    
    # Create test data
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    
    # Run kernel (simulated as data * 2)
    result = bridge.run_sycl_kernel("// SYCL kernel", data)
    
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.shape == data.shape


def test_benchmark():
    """Test oneAPI benchmarking"""
    bridge = OneAPIBridge()
    
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
