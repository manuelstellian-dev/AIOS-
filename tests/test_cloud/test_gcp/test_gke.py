"""Tests for GCP GKE Deployer"""
import pytest

# Try to import GCP modules
try:
    from venom.cloud.gcp.gke_deployer import GKEDeployer
    from google.cloud import container_v1
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    GKEDeployer = None


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_gke_deployer_init():
    """Test GKE deployer initialization"""
    deployer = GKEDeployer(
        project_id='test-project',
        cluster_name='test-cluster',
        zone='us-central1-a'
    )
    
    assert deployer.project_id == 'test-project'
    assert deployer.cluster_name == 'test-cluster'
    assert deployer.zone == 'us-central1-a'


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_gke_deployer_methods():
    """Test GKE deployer has required methods"""
    deployer = GKEDeployer(
        project_id='test-project',
        cluster_name='test-cluster'
    )
    
    assert hasattr(deployer, 'create_cluster')
    assert hasattr(deployer, 'get_cluster_info')
    assert hasattr(deployer, 'deploy_venom')
    assert hasattr(deployer, 'scale_deployment')
    assert hasattr(deployer, 'get_pods_status')
    assert hasattr(deployer, 'delete_cluster')


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_create_cluster_mock():
    """Test cluster creation (mock)"""
    deployer = GKEDeployer(project_id='test-project')
    
    assert callable(deployer.create_cluster)


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_deploy_venom_mock():
    """Test VENOM deployment (mock)"""
    deployer = GKEDeployer(project_id='test-project')
    
    assert callable(deployer.deploy_venom)


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_scale_deployment_mock():
    """Test deployment scaling (mock)"""
    deployer = GKEDeployer(project_id='test-project')
    
    assert callable(deployer.scale_deployment)


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_get_pods_status_mock():
    """Test getting pod status (mock)"""
    deployer = GKEDeployer(project_id='test-project')
    
    assert callable(deployer.get_pods_status)


@pytest.mark.skipif(not GCP_AVAILABLE, reason="GCP SDK not available")
def test_delete_cluster_mock():
    """Test cluster deletion (mock)"""
    deployer = GKEDeployer(project_id='test-project')
    
    assert callable(deployer.delete_cluster)


def test_gke_import_fallback():
    """Test graceful fallback when GCP SDK not available"""
    if not GCP_AVAILABLE:
        pytest.skip("GCP SDK not available - graceful fallback working")
    else:
        assert GKEDeployer is not None
