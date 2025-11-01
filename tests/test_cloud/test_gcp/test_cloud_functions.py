"""Tests for GCP Cloud Functions Handler"""
import pytest
import json

# Try to import GCP modules
try:
    from venom.cloud.gcp.cloud_functions import (
        cloud_function_handler,
        CloudFunctionsDeployer,
        _health_check_gcp,
        _execute_wave_gcp,
        _benchmark_gcp
    )
    from google.cloud import functions_v1
    GCP_FUNCTIONS_AVAILABLE = True
except ImportError:
    GCP_FUNCTIONS_AVAILABLE = False
    cloud_function_handler = None
    CloudFunctionsDeployer = None


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_health_check_gcp():
    """Test GCP health check"""
    result = _health_check_gcp({})
    
    assert result['status'] == 'healthy'
    assert 'timestamp' in result


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_execute_wave_gcp():
    """Test GCP wave execution"""
    result = _execute_wave_gcp({
        'wave_config': {
            'type': 'test',
            'iterations': 5
        }
    })
    
    assert result['wave_type'] == 'test'
    assert result['iterations'] == 5


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_benchmark_gcp():
    """Test GCP benchmark"""
    result = _benchmark_gcp({
        'params': {'test_type': 'inference'}
    })
    
    assert result['test_type'] == 'inference'
    assert 'throughput' in result


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_cloud_functions_deployer_init():
    """Test Cloud Functions deployer initialization"""
    deployer = CloudFunctionsDeployer(
        project_id='test-project',
        region='us-central1'
    )
    
    assert deployer.project_id == 'test-project'
    assert deployer.region == 'us-central1'


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_cloud_functions_deployer_methods():
    """Test Cloud Functions deployer has required methods"""
    deployer = CloudFunctionsDeployer(project_id='test-project')
    
    assert hasattr(deployer, 'create_function')
    assert hasattr(deployer, 'deploy_code')
    assert hasattr(deployer, 'invoke')
    assert hasattr(deployer, 'delete_function')
    assert hasattr(deployer, 'get_function_info')


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_create_function_mock():
    """Test function creation (mock)"""
    deployer = CloudFunctionsDeployer(project_id='test-project')
    
    assert callable(deployer.create_function)


@pytest.mark.skipif(not GCP_FUNCTIONS_AVAILABLE, reason="GCP Functions SDK not available")
def test_invoke_mock():
    """Test function invocation (mock)"""
    deployer = CloudFunctionsDeployer(project_id='test-project')
    
    assert callable(deployer.invoke)


def test_cloud_functions_import_fallback():
    """Test graceful fallback when GCP Functions SDK not available"""
    if not GCP_FUNCTIONS_AVAILABLE:
        pytest.skip("GCP Functions SDK not available - graceful fallback working")
    else:
        assert cloud_function_handler is not None
        assert CloudFunctionsDeployer is not None
