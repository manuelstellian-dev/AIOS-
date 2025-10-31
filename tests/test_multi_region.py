"""Test Multi-Region Deployment"""
import pytest
from venom.deployment.multi_region import MultiRegionManager, Region

def test_multi_region_register():
    """Test region registration"""
    manager = MultiRegionManager()
    
    region = Region(
        region_id="us-west",
        name="US West",
        lat=37.7749,
        lon=-122.4194,
        edge_nodes=["node1", "node2"],
        status="active"
    )
    
    assert manager.register_region(region) == True
    assert "us-west" in manager.regions
    assert manager.get_region_status("us-west") == "active"
    
    # Cannot register same region twice
    assert manager.register_region(region) == False

def test_multi_region_cross_region_deploy():
    """Test cross-region deployment"""
    manager = MultiRegionManager()
    
    # Register two regions
    region1 = Region(
        region_id="us-west",
        name="US West",
        lat=37.7749,
        lon=-122.4194,
        edge_nodes=["node1"],
        status="active"
    )
    region2 = Region(
        region_id="us-east",
        name="US East",
        lat=40.7128,
        lon=-74.0060,
        edge_nodes=["node2"],
        status="active"
    )
    
    manager.register_region(region1)
    manager.register_region(region2)
    
    # Deploy from west to east
    success = manager.cross_region_deploy("deploy1", "us-west", "us-east")
    assert success == True
    assert "deploy1" in manager.deployments
    assert manager.deployments["deploy1"] == "us-east"
    
    # Cannot deploy to non-existent region
    success = manager.cross_region_deploy("deploy2", "us-west", "eu-west")
    assert success == False

def test_multi_region_failover():
    """Test region failover to nearest region"""
    manager = MultiRegionManager()
    
    # Register three regions
    region1 = Region(
        region_id="us-west",
        name="US West",
        lat=37.7749,
        lon=-122.4194,
        edge_nodes=["node1"],
        status="active"
    )
    region2 = Region(
        region_id="us-east",
        name="US East",
        lat=40.7128,
        lon=-74.0060,
        edge_nodes=["node2"],
        status="active"
    )
    region3 = Region(
        region_id="eu-west",
        name="EU West",
        lat=51.5074,
        lon=-0.1278,
        edge_nodes=["node3"],
        status="active"
    )
    
    manager.register_region(region1)
    manager.register_region(region2)
    manager.register_region(region3)
    
    # Failover from us-west should go to us-east (closer than eu-west)
    failover_target = manager.region_failover("us-west")
    assert failover_target == "us-east"
    assert manager.get_region_status("us-west") == "offline"

def test_multi_region_latency_routing():
    """Test latency-based routing to nearest region"""
    manager = MultiRegionManager()
    
    # Register regions
    region1 = Region(
        region_id="us-west",
        name="US West",
        lat=37.7749,
        lon=-122.4194,
        edge_nodes=["node1"],
        status="active"
    )
    region2 = Region(
        region_id="us-east",
        name="US East",
        lat=40.7128,
        lon=-74.0060,
        edge_nodes=["node2"],
        status="active"
    )
    
    manager.register_region(region1)
    manager.register_region(region2)
    
    # Client in San Francisco should route to us-west
    nearest = manager.latency_based_routing(37.7749, -122.4194)
    assert nearest == "us-west"
    
    # Client in New York should route to us-east
    nearest = manager.latency_based_routing(40.7128, -74.0060)
    assert nearest == "us-east"
    
    # Client in Chicago (closer to us-east) should route to us-east
    nearest = manager.latency_based_routing(41.8781, -87.6298)
    assert nearest == "us-east"
