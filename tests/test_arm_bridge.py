"""Test ARM Bridge"""
import pytest
from venom.hardware.arm_bridge import ARMBridge


def test_arm_detection():
    """Test ARM bridge initializes and detects availability"""
    bridge = ARMBridge()
    assert bridge is not None
    assert isinstance(bridge.is_available(), bool)
    
    # Check Raspberry Pi detection
    assert isinstance(bridge.is_raspberry_pi, bool)
    assert isinstance(bridge.gpio_available, bool)


def test_cpu_info():
    """Test getting ARM CPU info"""
    bridge = ARMBridge()
    info = bridge.get_cpu_info()
    
    assert isinstance(info, dict)
    assert "model" in info
    assert "cores" in info
    assert "architecture" in info
    assert "simulated" in info
    
    # Cores should be positive
    assert info["cores"] > 0


def test_neon_optimization():
    """Test NEON SIMD optimization check"""
    bridge = ARMBridge()
    
    result = bridge.optimize_neon()
    assert isinstance(result, bool)
    
    # If ARM is available, should check for NEON
    # Simulated mode returns True
    if not bridge.available:
        assert result == True


def test_temperature_monitoring():
    """Test temperature monitoring"""
    bridge = ARMBridge()
    
    temp = bridge.get_temperature()
    assert isinstance(temp, float)
    
    # Temperature should be reasonable or -1.0 if unavailable
    if temp != -1.0:
        assert temp > 0 and temp < 120  # Reasonable temperature range
    
    # Simulated mode returns 45.5°C
    if not bridge.available:
        assert temp == 45.5


def test_gpio_operations():
    """Test GPIO operations (simulated if not on Raspberry Pi)"""
    bridge = ARMBridge()
    
    # Test GPIO setup (should not raise errors)
    bridge.gpio_setup(17, 'OUT')
    bridge.gpio_setup(18, 'IN')
    
    # Test GPIO write (should not raise errors)
    bridge.gpio_write(17, 1)
    bridge.gpio_write(17, 0)
    
    # Test GPIO read (should return int)
    value = bridge.gpio_read(18)
    assert isinstance(value, int)
    assert value in [-1, 0, 1]  # -1 if unavailable, 0/1 if available
    
    # If not available, should return 0 (simulated)
    if not bridge.gpio_available:
        assert value == 0
    
    # Test GPIO cleanup (should not raise errors)
    bridge.gpio_cleanup()
