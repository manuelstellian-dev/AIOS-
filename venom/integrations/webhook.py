"""
VENOM Webhook Integration
Generic webhook integration for HTTP callbacks
"""
import json
import time
from typing import Dict, Tuple, Optional, Any

# Graceful import
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class WebhookIntegration:
    """
    Generic webhook integration for sending HTTP requests
    
    Features:
    - POST/PUT/PATCH support
    - JSON and form-encoded data
    - Custom headers
    - Basic authentication
    - Response tracking
    - Retry logic with exponential backoff
    
    Example:
        webhook = WebhookIntegration(
            url="https://api.example.com/webhook",
            headers={"X-API-Key": "secret"}
        )
        response = webhook.send_json({"event": "test", "data": "value"})
    """
    
    def __init__(
        self,
        url: str,
        headers: Dict[str, str] = None,
        auth: Tuple[str, str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize webhook integration
        
        Args:
            url: Webhook URL
            headers: Custom headers dict (optional)
            auth: Basic auth tuple (username, password) (optional)
            timeout: Request timeout in seconds (default: 10)
            max_retries: Maximum number of retries (default: 3)
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available. Install with: pip install requests>=2.31.0")
        
        self.url = url
        self.headers = headers or {}
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_response = None
    
    def send(
        self,
        data: Dict[str, Any],
        method: str = 'POST',
        retry: bool = True
    ) -> Dict[str, Any]:
        """
        Send data to webhook with specified HTTP method
        
        Args:
            data: Data to send (will be JSON-encoded)
            method: HTTP method (POST, PUT, PATCH)
            retry: Enable retry logic (default: True)
            
        Returns:
            Dict with 'ok', 'status_code', 'data', 'error' fields
        """
        method = method.upper()
        if method not in ['POST', 'PUT', 'PATCH']:
            return {"ok": False, "error": f"Unsupported method: {method}"}
        
        retries = 0
        last_error = None
        
        while retries <= (self.max_retries if retry else 0):
            try:
                response = requests.request(
                    method=method,
                    url=self.url,
                    json=data,
                    headers=self.headers,
                    auth=self.auth,
                    timeout=self.timeout
                )
                
                self.last_response = {
                    "ok": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": self._parse_response(response),
                    "headers": dict(response.headers),
                    "timestamp": time.time()
                }
                
                # Success
                if response.status_code < 400:
                    return self.last_response
                
                # Client error (4xx) - don't retry
                if 400 <= response.status_code < 500:
                    self.last_response["error"] = f"Client error: {response.status_code}"
                    return self.last_response
                
                # Server error (5xx) - retry
                last_error = f"Server error: {response.status_code}"
                
            except Exception as e:
                # Handle all request exceptions
                error_type = type(e).__name__
                if 'Timeout' in error_type:
                    last_error = "Request timeout"
                elif 'ConnectionError' in error_type:
                    last_error = "Connection error"
                else:
                    last_error = str(e)
            
            # Exponential backoff
            if retry and retries < self.max_retries:
                wait_time = (2 ** retries) * 0.5  # 0.5s, 1s, 2s, 4s...
                time.sleep(wait_time)
                retries += 1
            else:
                break
        
        # All retries failed
        self.last_response = {
            "ok": False,
            "error": last_error,
            "retries": retries,
            "timestamp": time.time()
        }
        return self.last_response
    
    def send_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON data via POST
        
        Args:
            data: Data dict to send as JSON
            
        Returns:
            Response dict
        """
        return self.send(data, method='POST')
    
    def send_form(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send form-encoded data via POST
        
        Args:
            data: Data dict to send as form data
            
        Returns:
            Response dict
        """
        try:
            response = requests.post(
                self.url,
                data=data,
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout
            )
            
            self.last_response = {
                "ok": response.status_code < 400,
                "status_code": response.status_code,
                "data": self._parse_response(response),
                "headers": dict(response.headers),
                "timestamp": time.time()
            }
            
            if response.status_code >= 400:
                self.last_response["error"] = f"HTTP error: {response.status_code}"
            
            return self.last_response
            
        except Exception as e:
            self.last_response = {
                "ok": False,
                "error": str(e),
                "timestamp": time.time()
            }
            return self.last_response
    
    def get_last_response(self) -> Optional[Dict[str, Any]]:
        """
        Get the last response received
        
        Returns:
            Last response dict or None
        """
        return self.last_response
    
    def _parse_response(self, response) -> Any:
        """Parse response data based on content type"""
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                return response.json()
            except Exception:
                return response.text
        else:
            return response.text
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if webhook integration is available (requests library installed)
        
        Returns:
            True if requests library is available
        """
        return REQUESTS_AVAILABLE
