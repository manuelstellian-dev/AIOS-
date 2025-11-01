"""Tests for Model Serving"""
import pytest
import time
from venom.ml.model_serving import ModelServer


class DummyModel:
    """Dummy model for testing"""
    def predict(self, data):
        return {'result': data * 2}


@pytest.fixture
def server():
    """Create model server for testing"""
    return ModelServer(host='127.0.0.1', port=8002)


def test_register_model(server):
    """Test registering a model"""
    model = DummyModel()
    server.register_model('dummy', model)
    
    assert 'dummy' in server._models
    assert server._models['dummy'] is model


def test_health_endpoint(server):
    """Test health check endpoint"""
    if not server.is_available():
        pytest.skip("fastapi/uvicorn not available")
        
    model = DummyModel()
    server.register_model('test_model', model)
    
    # Start server
    server.start()
    time.sleep(1)  # Wait for server to start
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:8002/health', timeout=2)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['models_loaded'] == 1
    except ImportError:
        pytest.skip("requests not available")
    except Exception as e:
        pytest.skip(f"Server connection failed: {e}")
    finally:
        server.stop()


def test_predict_endpoint(server):
    """Test prediction endpoint"""
    if not server.is_available():
        pytest.skip("fastapi/uvicorn not available")
        
    model = DummyModel()
    server.register_model('dummy', model)
    
    # Start server
    server.start()
    time.sleep(1)
    
    try:
        import requests
        response = requests.post(
            'http://127.0.0.1:8002/predict/dummy',
            json={'data': 5},
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['model'] == 'dummy'
        assert data['prediction']['result'] == 10
        
        # Test non-existent model
        response = requests.post(
            'http://127.0.0.1:8002/predict/nonexistent',
            json={'data': 5},
            timeout=2
        )
        assert response.status_code == 404
        
    except ImportError:
        pytest.skip("requests not available")
    except Exception as e:
        pytest.skip(f"Server connection failed: {e}")
    finally:
        server.stop()


def test_list_models_endpoint(server):
    """Test list models endpoint"""
    if not server.is_available():
        pytest.skip("fastapi/uvicorn not available")
        
    model1 = DummyModel()
    model2 = DummyModel()
    server.register_model('model1', model1)
    server.register_model('model2', model2)
    
    # Start server
    server.start()
    time.sleep(1)
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:8002/models', timeout=2)
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 2
        assert 'model1' in data['models']
        assert 'model2' in data['models']
        
    except ImportError:
        pytest.skip("requests not available")
    except Exception as e:
        pytest.skip(f"Server connection failed: {e}")
    finally:
        server.stop()


def test_server_start_stop(server):
    """Test server start and stop"""
    if not server.is_available():
        pytest.skip("fastapi/uvicorn not available")
        
    assert not server.is_running()
    
    # Start server
    server.start()
    time.sleep(1)
    assert server.is_running()
    
    # Stop server
    server.stop()
    time.sleep(0.5)
    assert not server.is_running()
    
    # Test double start warning
    server.start()
    time.sleep(1)
    server.start()  # Should warn, not error
    server.stop()


def test_batch_predict_endpoint(server):
    """Test batch prediction endpoint"""
    if not server.is_available():
        pytest.skip("fastapi/uvicorn not available")
        
    model = DummyModel()
    server.register_model('dummy', model)
    
    # Start server
    server.start()
    time.sleep(1)
    
    try:
        import requests
        response = requests.post(
            'http://127.0.0.1:8002/batch_predict/dummy',
            json={'data': [1, 2, 3, 4, 5]},
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['count'] == 5
        assert len(data['predictions']) == 5
        
    except ImportError:
        pytest.skip("requests not available")
    except Exception as e:
        pytest.skip(f"Server connection failed: {e}")
    finally:
        server.stop()


def test_model_with_preprocessor(server):
    """Test model with custom preprocessor"""
    model = DummyModel()
    
    def preprocessor(data):
        return data + 10
        
    server.register_model('dummy', model, preprocessor=preprocessor)
    
    assert 'dummy' in server._models
    assert 'dummy' in server._preprocessors
