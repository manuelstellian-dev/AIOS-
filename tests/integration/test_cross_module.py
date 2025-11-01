"""
Cross-module integration tests
"""
import pytest
from unittest.mock import Mock
from venom.core.arbiter import Arbiter
from venom.security.auth import MeshAuthenticator
from venom.security.encryption import AdvancedEncryption


class TestCoreSecurityIntegration:
    """Test integration between core and security modules"""
    
    def test_arbiter_with_authenticated_actions(self):
        """Test arbiter executing authenticated actions"""
        arbiter = Arbiter()
        auth = MeshAuthenticator()
        
        token = auth.generate_token("node-001")
        
        # Execute a beat which executes actions
        result = arbiter.execute_beat()
        
        assert result is not None
        assert "action" in result
    
    def test_arbiter_with_encrypted_data(self):
        """Test arbiter handling encrypted data"""
        arbiter = Arbiter()
        encryption = AdvancedEncryption(algorithm='aes-gcm')
        
        data = b"sensitive data"
        key = encryption.generate_key(algorithm='aes-gcm')
        encrypted = encryption.encrypt(data, key)
        decrypted = encryption.decrypt(encrypted, key)
        
        assert decrypted == data
        
        # Execute a beat
        result = arbiter.execute_beat()
        
        assert result is not None
    
    def test_ledger_with_integrity(self):
        """Test ledger integrity check"""
        arbiter = Arbiter()
        
        # Record action
        arbiter.ledger.record_action("TEST", {"data": "test"})
        
        # Verify chain
        is_valid = arbiter.ledger.verify_chain()
        
        assert is_valid == True


class TestFullStackIntegration:
    """Test full stack integration"""
    
    def test_complete_flow(self):
        """Test complete flow"""
        arbiter = Arbiter()
        auth = MeshAuthenticator()
        
        token = auth.generate_token("test-node")
        
        # Execute a beat
        result = arbiter.execute_beat()
        
        assert result is not None
        assert arbiter.ledger.get_chain_length() > 0
    
    def test_multi_module_beat(self):
        """Test beat involving multiple modules"""
        arbiter = Arbiter()
        
        beat_result = arbiter.execute_beat()
        
        assert beat_result is not None
        assert arbiter.beat_count > 0
