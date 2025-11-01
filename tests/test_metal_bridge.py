"""Test Metal Bridge"""
import pytest
from venom.hardware.metal_bridge import MetalBridge
import numpy as np


def test_metal_detection():
    """Test Metal bridge initializes and detects availability"""
    bridge = MetalBridge()
    assert bridge is not None
    assert isinstance(bridge.is_available(), bool)
    
    # Check Apple Silicon detection
    assert isinstance(bridge.is_apple_silicon, bool)


def test_device_info():
    """Test getting Metal device info"""
    bridge = MetalBridge()
    info = bridge.get_device_info()
    
    assert isinstance(info, dict)
    assert "name" in info
    assert "architecture" in info
    assert "simulated" in info
    
    # If simulated, should have expected fields
    if info["simulated"]:
        assert "gpu_cores" in info
        assert "neural_engine_cores" in info
        assert "unified_memory_gb" in info


def test_buffer_allocation():
    """Test Metal buffer allocation"""
    bridge = MetalBridge()
    size_mb = 10
    
    # Should allocate or simulate allocation
    buffer = bridge.allocate_buffer(size_mb)
    assert buffer is not None
    
    # If simulated, should be numpy array
    if not bridge.available:
        assert isinstance(buffer, np.ndarray)


def test_neural_engine():
    """Test Neural Engine optimization check"""
    bridge = MetalBridge()
    
    result = bridge.optimize_for_neural_engine()
    assert isinstance(result, bool)
    
    # If Metal is available on Apple Silicon, should return True
    if bridge.available and bridge.is_apple_silicon:
        assert result == True


def test_benchmark():
    """Test Metal benchmarking"""
    bridge = MetalBridge()
    
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
