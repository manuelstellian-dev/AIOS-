"""Test Edge Deployment"""
import pytest
from venom.deployment.edge_deploy import EdgeDeployer, EdgeNode

def test_edge_deploy_init():
    """Test edge deployer initializes"""
    deployer = EdgeDeployer()
    assert deployer is not None
    assert len(deployer.nodes) == 0

def test_edge_deploy_register_node():
    """Test node registration"""
    deployer = EdgeDeployer()
    
    node = EdgeNode(
        node_id="edge-1",
        host="192.168.1.100",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "gpu": 0}
    )
    
    deployer.register_node(node)
    assert "edge-1" in deployer.nodes
    assert deployer.get_node_status("edge-1") == "idle"

def test_edge_deploy_clone():
    """Test instance cloning"""
    deployer = EdgeDeployer()
    
    node = EdgeNode(
        node_id="edge-1",
        host="localhost",
        port=9000,
        resources={"cpu": 2, "memory": 4096}
    )
    
    deployer.register_node(node)
    result = deployer.clone_instance("edge-1")
    
    assert result == True
    assert deployer.get_node_status("edge-1") == "active"
    assert "edge-1" in deployer.deployments
