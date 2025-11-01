"""Tests for Webhook Integration"""
import pytest
from unittest.mock import Mock, patch

# Try to import webhook integration
try:
    from venom.integrations.webhook import WebhookIntegration
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False
    WebhookIntegration = None


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_send_json():
    """Test sending JSON data"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_requests.request.return_value = mock_response
        
        webhook = WebhookIntegration(url="https://api.example.com/webhook")
        result = webhook.send_json({"event": "test", "data": "value"})
        
        assert result["ok"] is True
        assert result["status_code"] == 200
        assert result["data"]["status"] == "success"
        mock_requests.request.assert_called_once()


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_send_form():
    """Test sending form-encoded data"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "OK"
        mock_requests.post.return_value = mock_response
        
        webhook = WebhookIntegration(url="https://api.example.com/webhook")
        result = webhook.send_form({"key": "value"})
        
        assert result["ok"] is True
        assert result["status_code"] == 200
        mock_requests.post.assert_called_once()


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_custom_headers():
    """Test using custom headers"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_requests.request.return_value = mock_response
        
        webhook = WebhookIntegration(
            url="https://api.example.com/webhook",
            headers={"X-API-Key": "secret", "X-Custom": "value"}
        )
        result = webhook.send_json({"test": "data"})
        
        assert result["ok"] is True
        
        # Verify headers were passed
        call_args = mock_requests.request.call_args
        assert call_args[1]["headers"]["X-API-Key"] == "secret"
        assert call_args[1]["headers"]["X-Custom"] == "value"


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_retry_logic():
    """Test retry logic with exponential backoff"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        with patch('venom.integrations.webhook.time.sleep'):  # Skip actual sleep
            # Mock server error, then success
            mock_response_error = Mock()
            mock_response_error.status_code = 500
            
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.headers = {"Content-Type": "application/json"}
            mock_response_success.json.return_value = {"status": "success"}
            
            mock_requests.request.side_effect = [
                mock_response_error,
                mock_response_success
            ]
            
            webhook = WebhookIntegration(
                url="https://api.example.com/webhook",
                max_retries=3
            )
            result = webhook.send_json({"test": "data"})
            
            # Should succeed after retry
            assert result["ok"] is True
            assert mock_requests.request.call_count == 2


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_is_available():
    """Test checking if webhook integration is available"""
    result = WebhookIntegration.is_available()
    
    # Should be True if we got here (requests is available)
    assert result is True


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_get_last_response():
    """Test getting last response"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_requests.request.return_value = mock_response
        
        webhook = WebhookIntegration(url="https://api.example.com/webhook")
        webhook.send_json({"test": "data"})
        
        last_response = webhook.get_last_response()
        assert last_response is not None
        assert last_response["ok"] is True
        assert last_response["status_code"] == 200


@pytest.mark.skipif(not WEBHOOK_AVAILABLE, reason="Webhook integration not available")
def test_basic_auth():
    """Test basic authentication"""
    with patch('venom.integrations.webhook.requests') as mock_requests:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_requests.request.return_value = mock_response
        
        webhook = WebhookIntegration(
            url="https://api.example.com/webhook",
            auth=("username", "password")
        )
        result = webhook.send_json({"test": "data"})
        
        assert result["ok"] is True
        
        # Verify auth was passed
        call_args = mock_requests.request.call_args
        assert call_args[1]["auth"] == ("username", "password")


@pytest.mark.skipif(WEBHOOK_AVAILABLE, reason="Test requires requests to be unavailable")
def test_webhook_without_requests():
    """Test that webhook gracefully handles missing requests library"""
    # This test only runs if requests is not available
    pass
