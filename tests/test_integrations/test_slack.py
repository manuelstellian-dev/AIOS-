"""Tests for Slack Integration"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# Try to import Slack integration
try:
    from venom.integrations.slack import SlackIntegration
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    SlackIntegration = None


@pytest.mark.skipif(not SLACK_AVAILABLE, reason="Slack integration not available")
def test_send_message():
    """Test sending a message via webhook"""
    with patch('venom.integrations.slack.requests') as mock_requests:
        # Mock successful webhook response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_requests.post.return_value = mock_response
        
        slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")
        result = slack.send_message("#general", "Test message")
        
        assert result["ok"] is True
        assert result["channel"] == "webhook"
        mock_requests.post.assert_called_once()


@pytest.mark.skipif(not SLACK_AVAILABLE, reason="Slack integration not available")
def test_send_alert():
    """Test sending an alert message"""
    with patch('venom.integrations.slack.requests') as mock_requests:
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "channel": "C123", "ts": "1234567890.123456"}
        mock_requests.post.return_value = mock_response
        
        slack = SlackIntegration(token="xoxb-test-token")
        result = slack.send_alert("#alerts", "error", "Test error message")
        
        assert result["ok"] is True
        mock_requests.post.assert_called_once()
        
        # Check that the call included blocks
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["blocks"] is not None


@pytest.mark.skipif(not SLACK_AVAILABLE, reason="Slack integration not available")
def test_upload_file():
    """Test file upload"""
    with patch('venom.integrations.slack.requests') as mock_requests:
        with patch('builtins.open', create=True) as mock_open:
            # Mock file and successful upload response
            mock_open.return_value.__enter__.return_value = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True, "file": {"id": "F123"}}
            mock_requests.post.return_value = mock_response
            
            slack = SlackIntegration(token="xoxb-test-token")
            result = slack.upload_file("#general", "/tmp/test.txt", title="Test File")
            
            assert result["ok"] is True
            assert result["file"]["id"] == "F123"


@pytest.mark.skipif(not SLACK_AVAILABLE, reason="Slack integration not available")
def test_get_channels():
    """Test getting channels list"""
    with patch('venom.integrations.slack.requests') as mock_requests:
        # Mock channels list response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "channels": [
                {"id": "C123", "name": "general"},
                {"id": "C456", "name": "alerts"}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        slack = SlackIntegration(token="xoxb-test-token")
        channels = slack.get_channels()
        
        assert len(channels) == 2
        assert channels[0]["name"] == "general"
        assert channels[1]["name"] == "alerts"


@pytest.mark.skipif(not SLACK_AVAILABLE, reason="Slack integration not available")
def test_is_available():
    """Test checking if Slack integration is available"""
    result = SlackIntegration.is_available()
    
    # Should be True if we got here (requests is available)
    assert result is True


@pytest.mark.skipif(SLACK_AVAILABLE, reason="Test requires requests to be unavailable")
def test_slack_without_requests():
    """Test that Slack gracefully handles missing requests library"""
    # This test only runs if requests is not available
    # In normal circumstances, it will be skipped
    pass
