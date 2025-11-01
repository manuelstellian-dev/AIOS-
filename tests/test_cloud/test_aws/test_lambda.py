"""Tests for AWS Lambda Handler"""
import pytest
import json

# Try to import AWS modules
try:
    from venom.cloud.aws.lambda_handler import (
        lambda_handler,
        LambdaDeployer,
        _health_check,
        _execute_wave,
        _benchmark
    )
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    lambda_handler = None
    LambdaDeployer = None


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_handler_health_check():
    """Test Lambda handler health check"""
    event = {'action': 'health_check'}
    
    # Mock context
    class MockContext:
        request_id = 'test-request-id'
    
    context = MockContext()
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['status'] == 'healthy'
    assert 'timestamp' in body


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_handler_execute_wave():
    """Test Lambda handler wave execution"""
    event = {
        'action': 'execute_wave',
        'wave_config': {
            'type': 'test',
            'iterations': 5
        }
    }
    
    class MockContext:
        request_id = 'test-request-id'
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['wave_type'] == 'test'
    assert body['iterations'] == 5


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_handler_benchmark():
    """Test Lambda handler benchmark"""
    event = {
        'action': 'benchmark',
        'params': {'test_type': 'inference'}
    }
    
    class MockContext:
        request_id = 'test-request-id'
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['test_type'] == 'inference'
    assert 'throughput' in body


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_deployer_init():
    """Test Lambda deployer initialization"""
    deployer = LambdaDeployer(region='us-east-1')
    
    assert deployer.region == 'us-east-1'
    assert deployer.lambda_client is not None


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_deployer_methods():
    """Test Lambda deployer has required methods"""
    deployer = LambdaDeployer(region='us-east-1')
    
    assert hasattr(deployer, 'create_function')
    assert hasattr(deployer, 'update_code')
    assert hasattr(deployer, 'invoke')
    assert hasattr(deployer, 'delete_function')
    assert callable(deployer.create_function)


@pytest.mark.skipif(not AWS_AVAILABLE, reason="AWS SDK not available")
def test_lambda_handler_invalid_action():
    """Test Lambda handler with invalid action"""
    event = {'action': 'invalid_action'}
    
    class MockContext:
        request_id = 'test-request-id'
    
    response = lambda_handler(event, MockContext())
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_import_fallback():
    """Test graceful fallback when AWS SDK not available"""
    if not AWS_AVAILABLE:
        pytest.skip("AWS SDK not available - graceful fallback working")
    else:
        assert lambda_handler is not None
        assert LambdaDeployer is not None
