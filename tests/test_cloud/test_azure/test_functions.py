"""Tests for Azure Functions Handler"""
import pytest
import json
import os

# Try to import Azure modules
try:
    from venom.cloud.azure.functions import (
        azure_function_handler,
        AzureFunctionsDeployer,
        _health_check_azure,
        _execute_wave_azure,
        _benchmark_azure
    )
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False
    azure_function_handler = None
    AzureFunctionsDeployer = None


@pytest.mark.skipif(not AZURE_FUNCTIONS_AVAILABLE, reason="Azure Functions SDK not available")
def test_health_check_azure():
    """Test Azure health check"""
    result = _health_check_azure({})
    
    assert result['status'] == 'healthy'
    assert 'timestamp' in result


@pytest.mark.skipif(not AZURE_FUNCTIONS_AVAILABLE, reason="Azure Functions SDK not available")
def test_execute_wave_azure():
    """Test Azure wave execution"""
    result = _execute_wave_azure({
        'wave_config': {
            'type': 'test',
            'iterations': 5
        }
    })
    
    assert result['wave_type'] == 'test'
    assert result['iterations'] == 5


@pytest.mark.skipif(not AZURE_FUNCTIONS_AVAILABLE, reason="Azure Functions SDK not available")
def test_benchmark_azure():
    """Test Azure benchmark"""
    result = _benchmark_azure({
        'params': {'test_type': 'inference'}
    })
    
    assert result['test_type'] == 'inference'
    assert 'throughput' in result


@pytest.mark.skipif(not AZURE_FUNCTIONS_AVAILABLE, reason="Azure Functions SDK not available")
def test_functions_deployer_init():
    """Test Functions deployer initialization"""
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AzureFunctionsDeployer(
            resource_group='test-rg',
            location='eastus'
        )
        
        assert deployer.resource_group == 'test-rg'
        assert deployer.location == 'eastus'
    except ValueError:
        pytest.skip("Azure credentials not configured")


@pytest.mark.skipif(not AZURE_FUNCTIONS_AVAILABLE, reason="Azure Functions SDK not available")
def test_functions_deployer_methods():
    """Test Functions deployer has required methods"""
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
    
    try:
        deployer = AzureFunctionsDeployer(resource_group='test-rg')
        
        assert hasattr(deployer, 'create_function_app')
        assert hasattr(deployer, 'deploy_code')
        assert hasattr(deployer, 'invoke')
        assert hasattr(deployer, 'delete_function_app')
    except ValueError:
        pytest.skip("Azure credentials not configured")


def test_azure_functions_import_fallback():
    """Test graceful fallback when Azure Functions SDK not available"""
    if not AZURE_FUNCTIONS_AVAILABLE:
        pytest.skip("Azure Functions SDK not available - graceful fallback working")
    else:
        assert azure_function_handler is not None
        assert AzureFunctionsDeployer is not None
