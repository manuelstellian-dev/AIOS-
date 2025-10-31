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

def test_edge_deploy_least_loaded_node():
    """Test finding least loaded node"""
    deployer = EdgeDeployer()
    
    # Node 1: High load
    node1 = EdgeNode(
        node_id="edge-1",
        host="192.168.1.100",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "gpu": 1, "cpu_usage": 3.5, "memory_usage": 7000, "gpu_usage": 0.8}
    )
    
    # Node 2: Low load
    node2 = EdgeNode(
        node_id="edge-2",
        host="192.168.1.101",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "gpu": 1, "cpu_usage": 1.0, "memory_usage": 2000, "gpu_usage": 0.2}
    )
    
    deployer.register_node(node1)
    deployer.register_node(node2)
    
    least_loaded = deployer.get_least_loaded_node()
    assert least_loaded == "edge-2"

def test_edge_deploy_with_load_balancing():
    """Test deployment with load balancing"""
    deployer = EdgeDeployer()
    
    node1 = EdgeNode(
        node_id="edge-1",
        host="192.168.1.100",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "cpu_usage": 3.0, "memory_usage": 6000}
    )
    
    node2 = EdgeNode(
        node_id="edge-2",
        host="192.168.1.101",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "cpu_usage": 1.0, "memory_usage": 2000}
    )
    
    deployer.register_node(node1)
    deployer.register_node(node2)
    
    deployed_node = deployer.deploy_with_load_balancing()
    assert deployed_node == "edge-2"
    assert deployer.get_node_status("edge-2") == "active"

def test_edge_deploy_cluster_stats():
    """Test cluster statistics"""
    deployer = EdgeDeployer()
    
    node1 = EdgeNode(
        node_id="edge-1",
        host="192.168.1.100",
        port=9000,
        resources={"cpu": 4, "memory": 8192, "gpu": 1}
    )
    
    node2 = EdgeNode(
        node_id="edge-2",
        host="192.168.1.101",
        port=9000,
        resources={"cpu": 8, "memory": 16384, "gpu": 2}
    )
    
    deployer.register_node(node1)
    deployer.register_node(node2)
    deployer.clone_instance("edge-1")
    
    stats = deployer.get_cluster_stats()
    assert stats["total_nodes"] == 2
    assert stats["active_nodes"] == 1
    assert stats["total_cpu"] == 12
    assert stats["total_memory"] == 24576
    assert stats["total_gpu"] == 3
    assert stats["total_deployments"] == 1
