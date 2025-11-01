"""
VENOM Slack Integration
Slack integration for notifications via webhooks and Web API
"""
import json
import time
from typing import Dict, List, Optional, Any

# Graceful import
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class SlackIntegration:
    """
    Slack integration for sending messages and notifications
    
    Features:
    - Webhook URL support (incoming webhooks)
    - Bot token support (Web API)
    - Message formatting with blocks
    - Alert types (info, warning, error, success)
    - File upload support
    - Channel listing
    
    Example:
        # Using webhook URL
        slack = SlackIntegration(webhook_url="https://hooks.slack.com/...")
        slack.send_message("#general", "Hello from VENOM!")
        
        # Using bot token
        slack = SlackIntegration(token="xoxb-...")
        slack.send_alert("#alerts", "error", "System failure detected")
    """
    
    def __init__(self, webhook_url: str = None, token: str = None):
        """
        Initialize Slack integration
        
        Args:
            webhook_url: Slack incoming webhook URL (optional)
            token: Slack bot token (xoxb-...) (optional)
        """
        self.webhook_url = webhook_url
        self.token = token
        self.api_base = "https://api.slack.com/api"
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available. Install with: pip install requests>=2.31.0")
        
        if not webhook_url and not token:
            raise ValueError("Either webhook_url or token must be provided")
    
    def send_message(
        self, 
        channel: str, 
        text: str, 
        blocks: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel
        
        Args:
            channel: Channel name (e.g., "#general") or ID
            text: Message text (fallback for notifications)
            blocks: Optional list of Block Kit blocks for rich formatting
            
        Returns:
            Response dict with 'ok' status and message details
        """
        if self.webhook_url:
            return self._send_via_webhook(text, blocks)
        elif self.token:
            return self._send_via_api(channel, text, blocks)
        else:
            return {"ok": False, "error": "No webhook URL or token configured"}
    
    def _send_via_webhook(self, text: str, blocks: List[Dict] = None) -> Dict[str, Any]:
        """Send message via webhook URL"""
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 and response.text == "ok":
                return {"ok": True, "channel": "webhook"}
            else:
                return {
                    "ok": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _send_via_api(
        self, 
        channel: str, 
        text: str, 
        blocks: List[Dict] = None
    ) -> Dict[str, Any]:
        """Send message via Slack Web API"""
        url = f"{self.api_base}/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": text
        }
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def send_alert(
        self, 
        channel: str, 
        alert_type: str, 
        message: str
    ) -> Dict[str, Any]:
        """
        Send a formatted alert message
        
        Args:
            channel: Channel name or ID
            alert_type: Type of alert (info, warning, error, success)
            message: Alert message
            
        Returns:
            Response dict with 'ok' status
        """
        # Alert colors and emojis
        alert_config = {
            "info": {"color": "#36a64f", "emoji": ":information_source:"},
            "warning": {"color": "#ff9900", "emoji": ":warning:"},
            "error": {"color": "#ff0000", "emoji": ":x:"},
            "success": {"color": "#00ff00", "emoji": ":white_check_mark:"}
        }
        
        config = alert_config.get(alert_type, alert_config["info"])
        text = f"{config['emoji']} *{alert_type.upper()}*: {message}"
        
        # Build blocks for rich formatting
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Sent from VENOM at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        return self.send_message(channel, text, blocks)
    
    def upload_file(
        self, 
        channel: str, 
        file_path: str, 
        title: str = None
    ) -> Dict[str, Any]:
        """
        Upload a file to a Slack channel
        
        Args:
            channel: Channel name or ID
            file_path: Path to file to upload
            title: Optional file title
            
        Returns:
            Response dict with 'ok' status and file details
        """
        if not self.token:
            return {"ok": False, "error": "File upload requires bot token"}
        
        url = f"{self.api_base}/files.upload"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'channels': channel}
                if title:
                    data['title'] = title
                
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30
                )
                return response.json()
        except FileNotFoundError:
            return {"ok": False, "error": f"File not found: {file_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """
        Get list of channels the bot has access to
        
        Returns:
            List of channel dicts with id, name, etc.
        """
        if not self.token:
            return []
        
        url = f"{self.api_base}/conversations.list"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if data.get("ok"):
                return data.get("channels", [])
            else:
                return []
        except Exception:
            return []
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Slack integration is available (requests library installed)
        
        Returns:
            True if requests library is available
        """
        return REQUESTS_AVAILABLE
