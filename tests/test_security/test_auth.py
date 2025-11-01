"""
Tests for Mesh Authentication Module
"""
import pytest
import time
import jwt
from venom.security.auth import MeshAuthenticator


class TestMeshAuthenticator:
    """Test MeshAuthenticator functionality"""
    
    def test_initialization(self):
        """Test authenticator initialization"""
        auth = MeshAuthenticator()
        
        assert auth.secret == "venom-secret-key"
        assert auth.algorithm == "HS256"
        assert auth.token_expiry == 3600
    
    def test_initialization_custom_params(self):
        """Test authenticator with custom parameters"""
        auth = MeshAuthenticator(
            secret="custom-secret",
            algorithm="HS512",
            token_expiry=7200
        )
        
        assert auth.secret == "custom-secret"
        assert auth.algorithm == "HS512"
        assert auth.token_expiry == 7200
    
    def test_generate_token(self):
        """Test token generation"""
        auth = MeshAuthenticator()
        token = auth.generate_token("node-001")
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode to verify contents
        payload = jwt.decode(token, auth.secret, algorithms=[auth.algorithm])
        assert payload['node_id'] == "node-001"
        assert 'iat' in payload
        assert 'exp' in payload
        assert payload['metadata'] == {}
    
    def test_generate_token_with_metadata(self):
        """Test token generation with metadata"""
        auth = MeshAuthenticator()
        metadata = {
            "role": "coordinator",
            "region": "us-east-1",
            "version": "1.0.0"
        }
        token = auth.generate_token("node-002", metadata=metadata)
        
        payload = jwt.decode(token, auth.secret, algorithms=[auth.algorithm])
        assert payload['node_id'] == "node-002"
        assert payload['metadata'] == metadata
        assert payload['metadata']['role'] == "coordinator"
    
    def test_validate_token_success(self):
        """Test successful token validation"""
        auth = MeshAuthenticator()
        token = auth.generate_token("node-003")
        
        result = auth.validate_token(token)
        
        assert result is not None
        assert result['node_id'] == "node-003"
        assert 'iat' in result
        assert 'exp' in result
    
    def test_validate_token_with_metadata(self):
        """Test validation of token with metadata"""
        auth = MeshAuthenticator()
        metadata = {"tier": "premium"}
        token = auth.generate_token("node-004", metadata=metadata)
        
        result = auth.validate_token(token)
        
        assert result is not None
        assert result['metadata'] == metadata
    
    def test_validate_expired_token(self):
        """Test validation of expired token"""
        auth = MeshAuthenticator(token_expiry=1)
        token = auth.generate_token("node-005")
        
        # Wait for token to expire
        time.sleep(2)
        
        result = auth.validate_token(token)
        assert result is None
    
    def test_validate_invalid_token(self):
        """Test validation of invalid token"""
        auth = MeshAuthenticator()
        
        result = auth.validate_token("invalid.token.here")
        assert result is None
    
    def test_validate_token_wrong_secret(self):
        """Test validation with wrong secret"""
        auth1 = MeshAuthenticator(secret="secret1")
        auth2 = MeshAuthenticator(secret="secret2")
        
        token = auth1.generate_token("node-006")
        
        # Try to validate with different authenticator
        result = auth2.validate_token(token)
        assert result is None
    
    def test_validate_token_wrong_algorithm(self):
        """Test validation with wrong algorithm"""
        auth1 = MeshAuthenticator(algorithm="HS256")
        token = auth1.generate_token("node-007")
        
        auth2 = MeshAuthenticator(algorithm="HS512")
        result = auth2.validate_token(token)
        
        # Should fail because algorithm doesn't match
        assert result is None
    
    def test_validate_empty_token(self):
        """Test validation of empty token"""
        auth = MeshAuthenticator()
        
        result = auth.validate_token("")
        assert result is None
    
    def test_authenticate_message_success(self):
        """Test successful message authentication"""
        auth = MeshAuthenticator()
        token = auth.generate_token("node-008")
        
        message = {"data": "test", "token": token, "sender_id": "node-008"}
        result = auth.authenticate_message(message)
        
        assert result is True
    
    def test_authenticate_message_no_token(self):
        """Test message authentication without token"""
        auth = MeshAuthenticator()
        message = {"data": "test"}
        
        result = auth.authenticate_message(message)
        assert result is False
    
    def test_authenticate_message_invalid_token(self):
        """Test message authentication with invalid token"""
        auth = MeshAuthenticator()
        message = {"data": "test", "token": "invalid"}
        
        result = auth.authenticate_message(message)
        assert result is False
    
    def test_authenticate_message_expired_token(self):
        """Test message authentication with expired token"""
        auth = MeshAuthenticator(token_expiry=1)
        token = auth.generate_token("node-009")
        
        time.sleep(2)
        
        message = {"data": "test", "token": token, "sender_id": "node-009"}
        result = auth.authenticate_message(message)
        
        assert result is False
    
    def test_authenticate_message_sender_mismatch(self):
        """Test message authentication with mismatched sender_id"""
        auth = MeshAuthenticator()
        token = auth.generate_token("node-010")
        
        # Token is for node-010 but message claims to be from node-011
        message = {"data": "test", "token": token, "sender_id": "node-011"}
        result = auth.authenticate_message(message)
        
        assert result is False
    
    def test_add_auth_to_message(self):
        """Test adding authentication to message"""
        auth = MeshAuthenticator()
        message = {"data": "test", "sender_id": "node-010"}
        
        auth.add_auth_to_message(message, "node-010")
        
        assert "token" in message
        # Verify the token is valid
        payload = auth.validate_token(message["token"])
        assert payload is not None
        assert payload['node_id'] == "node-010"
    
    def test_log_auth_attempt_success(self):
        """Test logging successful auth attempt"""
        auth = MeshAuthenticator()
        
        # Should not raise exception
        auth.log_auth_attempt("node-011", True)
    
    def test_log_auth_attempt_failure(self):
        """Test logging failed auth attempt"""
        auth = MeshAuthenticator()
        
        # Should not raise exception
        auth.log_auth_attempt("node-012", False, "Token expired")
    
    def test_token_expiry_timing(self):
        """Test that token expiry is respected"""
        auth = MeshAuthenticator(token_expiry=2)
        token = auth.generate_token("node-011")
        
        # Should be valid immediately
        result1 = auth.validate_token(token)
        assert result1 is not None
        
        # Wait 1 second (still valid)
        time.sleep(1)
        result2 = auth.validate_token(token)
        assert result2 is not None
        
        # Wait another 2 seconds (now expired)
        time.sleep(2)
        result3 = auth.validate_token(token)
        assert result3 is None
    
    def test_multiple_tokens_same_node(self):
        """Test generating multiple tokens for same node"""
        auth = MeshAuthenticator()
        
        token1 = auth.generate_token("node-012")
        time.sleep(1.1)  # Wait at least 1 second for timestamp to change
        token2 = auth.generate_token("node-012")
        
        # Both should be valid
        result1 = auth.validate_token(token1)
        result2 = auth.validate_token(token2)
        
        assert result1 is not None
        assert result2 is not None
        
        # They should be different tokens (different timestamps)
        assert token1 != token2
    
    def test_token_contains_correct_claims(self):
        """Test that token contains all required claims"""
        auth = MeshAuthenticator()
        token = auth.generate_token("node-013", metadata={"key": "value"})
        
        payload = jwt.decode(token, auth.secret, algorithms=[auth.algorithm])
        
        # Check all required claims
        assert 'node_id' in payload
        assert 'iat' in payload
        assert 'exp' in payload
        assert 'metadata' in payload
        
        # Check values
        assert payload['node_id'] == "node-013"
        assert payload['metadata']['key'] == "value"
        assert payload['exp'] > payload['iat']
        assert payload['exp'] == payload['iat'] + auth.token_expiry
