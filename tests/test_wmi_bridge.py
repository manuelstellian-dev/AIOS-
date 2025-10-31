"""Test WMI Bridge"""
import pytest
from venom.hardware.wmi_bridge import WMIBridge

def test_wmi_bridge_init():
    """Test WMI bridge initializes"""
    bridge = WMIBridge()
    assert bridge is not None

def test_wmi_bridge_temperature():
    """Test temperature reading (simulated on non-Windows)"""
    bridge = WMIBridge()
    temp = bridge.get_cpu_temperature()
    
    # Should return either real temp or simulated 55.0
    assert temp is not None
    assert isinstance(temp, float)
    assert 0 < temp < 150  # Reasonable temperature range

def test_wmi_bridge_system_info():
    """Test system info reading"""
    bridge = WMIBridge()
    info = bridge.get_system_info()
    
    assert info is not None
    assert isinstance(info, dict)
    assert len(info) > 0
