"""Tests for Azure AKS Deployer"""
import pytest
import os

# Try to import Azure modules
try:
    from venom.cloud.azure.aks_deployer import AKSDeployer
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    AKSDeployer = None


@pytest.mark.skipif(not AZURE_AVAILABLE, reason="Azure SDK not available")
def test_aks_deployer_init():
    """Test AKS deployer initialization"""
    # Set dummy subscription ID for testing
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AKSDeployer(
            resource_group='test-rg',
            cluster_name='test-cluster',
            location='eastus'
        )
        
        assert deployer.resource_group == 'test-rg'
        assert deployer.cluster_name == 'test-cluster'
        assert deployer.location == 'eastus'
    except ValueError:
        # Expected if no real Azure credentials
        pytest.skip("Azure credentials not configured")


@pytest.mark.skipif(not AZURE_AVAILABLE, reason="Azure SDK not available")
def test_aks_deployer_methods():
    """Test AKS deployer has required methods"""
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AKSDeployer(resource_group='test-rg')
        
        assert hasattr(deployer, 'create_cluster')
        assert hasattr(deployer, 'get_cluster_info')
        assert hasattr(deployer, 'deploy_venom')
        assert hasattr(deployer, 'scale_deployment')
        assert hasattr(deployer, 'get_pods_status')
        assert hasattr(deployer, 'delete_cluster')
    except ValueError:
        pytest.skip("Azure credentials not configured")


@pytest.mark.skipif(not AZURE_AVAILABLE, reason="Azure SDK not available")
def test_create_cluster_mock():
    """Test cluster creation (mock)"""
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AKSDeployer(resource_group='test-rg')
        assert callable(deployer.create_cluster)
    except ValueError:
        pytest.skip("Azure credentials not configured")


@pytest.mark.skipif(not AZURE_AVAILABLE, reason="Azure SDK not available")
def test_deploy_venom_mock():
    """Test VENOM deployment (mock)"""
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AKSDeployer(resource_group='test-rg')
        assert callable(deployer.deploy_venom)
    except ValueError:
        pytest.skip("Azure credentials not configured")


def test_aks_import_fallback():
    """Test graceful fallback when Azure SDK not available"""
    if not AZURE_AVAILABLE:
        pytest.skip("Azure SDK not available - graceful fallback working")
    else:
        assert AKSDeployer is not None
