"""
Mesh Authentication Module using JWT
Provides authentication for P2P mesh nodes
"""
import jwt
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MeshAuthenticator:
    """
    JWT-based authentication for P2P mesh
    
    Features:
    - JWT token generation
    - Token validation
    - HS256 algorithm
    - Reject unauthenticated messages
    - Log authentication attempts
    """
    
    def __init__(self, secret: str = "venom-secret-key", algorithm: str = "HS256", 
                 token_expiry: int = 3600):
        """
        Initialize mesh authenticator
        
        Args:
            secret: Secret key for JWT signing
            algorithm: JWT algorithm (default: HS256)
            token_expiry: Token expiry in seconds (default: 1 hour)
        """
        self.secret = secret
        self.algorithm = algorithm
        self.token_expiry = token_expiry
        
        logger.info(f"Mesh authenticator initialized (algorithm: {algorithm})")
    
    def generate_token(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate JWT token for a node
        
        Args:
            node_id: Node identifier
            metadata: Optional metadata to include in token
            
        Returns:
            JWT token string
        """
        now = int(time.time())
        
        payload = {
            "node_id": node_id,
            "iat": now,  # Issued at
            "exp": now + self.token_expiry,  # Expiration
            "metadata": metadata or {}
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        
        logger.debug(f"Generated token for node {node_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token
        
        Args:
            token: JWT token to validate
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            node_id = payload.get("node_id")
            logger.debug(f"Token validated for node {node_id}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def authenticate_message(self, message: Dict[str, Any]) -> bool:
        """
        Authenticate a mesh message
        
        Args:
            message: Message containing 'token' field
            
        Returns:
            True if authenticated, False otherwise
        """
        token = message.get("token")
        
        if not token:
            logger.warning("Message missing authentication token")
            return False
        
        payload = self.validate_token(token)
        
        if not payload:
            logger.warning(f"Authentication failed for message from {message.get('sender_id', 'unknown')}")
            return False
        
        # Verify sender_id matches token
        token_node_id = payload.get("node_id")
        message_node_id = message.get("sender_id")
        
        if token_node_id != message_node_id:
            logger.warning(f"Token node_id mismatch: {token_node_id} != {message_node_id}")
            return False
        
        logger.debug(f"Message authenticated from node {token_node_id}")
        return True
    
    def add_auth_to_message(self, message: Dict[str, Any], node_id: str):
        """
        Add authentication token to a message
        
        Args:
            message: Message to add token to
            node_id: Node ID for token generation
        """
        token = self.generate_token(node_id)
        message["token"] = token
    
    def log_auth_attempt(self, node_id: str, success: bool, reason: Optional[str] = None):
        """
        Log an authentication attempt
        
        Args:
            node_id: Node ID attempting authentication
            success: Whether authentication succeeded
            reason: Optional reason for failure
        """
        if success:
            logger.info(f"AUTH SUCCESS: Node {node_id} authenticated")
        else:
            logger.warning(f"AUTH FAILURE: Node {node_id} - {reason or 'Unknown reason'}")
