"""Test TPU Bridge"""
import pytest
from venom.hardware.tpu_bridge import TPUBridge

def test_tpu_bridge_init():
    """Test TPU bridge initializes"""
    bridge = TPUBridge()
    assert bridge is not None

def test_tpu_bridge_get_tpu_count():
    """Test getting TPU count (graceful fallback)"""
    bridge = TPUBridge()
    count = bridge.get_tpu_count()
    
    # Should return either actual TPU count or simulated value (8)
    assert isinstance(count, int)
    assert count >= 0
    
    # If TPU not available, should return simulated value
    if not bridge.available:
        assert count == 8

def test_tpu_bridge_get_tpu_info():
    """Test getting TPU info"""
    bridge = TPUBridge()
    info = bridge.get_tpu_info(0)
    
    assert isinstance(info, dict)
    assert "device_id" in info
    assert "version" in info
    assert "cores" in info
    assert "memory_gb" in info
    assert "architecture" in info
    assert "simulated" in info
    
    # Check version format
    assert isinstance(info["version"], str)
    assert info["cores"] > 0
    assert info["memory_gb"] > 0

def test_tpu_bridge_get_tpu_topology():
    """Test getting TPU topology"""
    bridge = TPUBridge()
    topology = bridge.get_tpu_topology()
    
    assert isinstance(topology, dict)
    assert "chip_count" in topology
    assert "mesh_shape" in topology
    assert "topology" in topology
    assert "devices" in topology
    assert "simulated" in topology
    
    # Verify mesh shape is a list
    assert isinstance(topology["mesh_shape"], list)
    assert len(topology["mesh_shape"]) >= 1
    
    # Verify chip count matches device list
    assert topology["chip_count"] == len(topology["devices"])

def test_tpu_bridge_is_tpu_v4_or_later():
    """Test TPU version check"""
    bridge = TPUBridge()
    is_v4_plus = bridge.is_tpu_v4_or_later()
    
    assert isinstance(is_v4_plus, bool)
    
    # If TPU not available, should return False (simulated is v3)
    if not bridge.available:
        assert is_v4_plus == False
