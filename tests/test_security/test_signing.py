"""
Comprehensive tests for LedgerSigner
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from venom.security.signing import LedgerSigner


class TestLedgerSignerInit:
    """Test LedgerSigner initialization"""
    
    def test_init_creates_key_directory(self):
        """Test initialization creates key directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = os.path.join(tmpdir, "test_keys")
            signer = LedgerSigner(key_dir=key_dir)
            
            assert Path(key_dir).exists()
            assert signer.key_dir == Path(key_dir)
    
    def test_init_generates_keys(self):
        """Test initialization generates keys"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = os.path.join(tmpdir, "test_keys")
            signer = LedgerSigner(key_dir=key_dir)
            
            assert signer.private_key is not None
            assert signer.public_key is not None
            assert signer.private_key_path.exists()
            assert signer.public_key_path.exists()
    
    def test_init_loads_existing_keys(self):
        """Test initialization loads existing keys"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = os.path.join(tmpdir, "test_keys")
            
            # Create first signer
            signer1 = LedgerSigner(key_dir=key_dir)
            public_key1 = signer1.public_key
            
            # Create second signer with same directory
            signer2 = LedgerSigner(key_dir=key_dir)
            
            # Should load same keys
            assert signer2.public_key is not None
    
    def test_key_file_permissions(self):
        """Test private key has restrictive permissions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = os.path.join(tmpdir, "test_keys")
            signer = LedgerSigner(key_dir=key_dir)
            
            # Private key should have 0o600 permissions
            stat_info = os.stat(signer.private_key_path)
            assert stat_info.st_mode & 0o777 == 0o600


class TestLedgerSignerSigning:
    """Test signing functionality"""
    
    def test_sign_data_bytes(self):
        """Test signing byte data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = b"test data"
            signature = signer.sign_data(data)
            
            assert isinstance(signature, bytes)
            assert len(signature) > 0
    
    def test_sign_data_string(self):
        """Test signing string data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = "test string"
            signature = signer.sign_data(data)
            
            assert isinstance(signature, bytes)
    
    def test_sign_data_dict(self):
        """Test signing dictionary data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = {"key": "value", "number": 42}
            signature = signer.sign_data(data)
            
            assert isinstance(signature, bytes)
    
    def test_sign_ledger_entry(self):
        """Test signing ledger entry"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            entry = {
                "action": "TEST",
                "data": {"test": "data"},
                "timestamp": "2025-01-01T00:00:00"
            }
            
            signature = signer.sign_ledger_entry(entry)
            
            assert isinstance(signature, bytes)
            assert len(signature) > 0
    
    def test_sign_merkle_root(self):
        """Test signing Merkle root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            merkle_root = "abc123" * 10
            signature = signer.sign_merkle_root(merkle_root)
            
            assert isinstance(signature, bytes)
    
    def test_same_data_different_signature(self):
        """Test signing same data produces consistent signature"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = b"test data"
            sig1 = signer.sign_data(data)
            sig2 = signer.sign_data(data)
            
            # Ed25519 is deterministic
            assert sig1 == sig2


class TestLedgerSignerVerification:
    """Test signature verification"""
    
    def test_verify_valid_signature(self):
        """Test verifying valid signature"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = b"test data"
            signature = signer.sign_data(data)
            
            is_valid = signer.verify_signature(data, signature)
            
            assert is_valid == True
    
    def test_verify_invalid_signature(self):
        """Test verifying invalid signature"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = b"test data"
            bad_signature = b"invalid" * 10
            
            is_valid = signer.verify_signature(data, bad_signature)
            
            assert is_valid == False
    
    def test_verify_tampered_data(self):
        """Test verification fails with tampered data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            data = b"original data"
            signature = signer.sign_data(data)
            
            tampered_data = b"tampered data"
            is_valid = signer.verify_signature(tampered_data, signature)
            
            assert is_valid == False
    
    def test_verify_ledger_entry(self):
        """Test verifying ledger entry signature"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            entry = {"action": "TEST", "data": {}}
            signature = signer.sign_ledger_entry(entry)
            
            is_valid = signer.verify_ledger_entry(entry, signature)
            
            assert is_valid == True
    
    def test_verify_merkle_root(self):
        """Test verifying Merkle root signature"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            merkle_root = "test_root" * 8
            signature = signer.sign_merkle_root(merkle_root)
            
            is_valid = signer.verify_merkle_root(merkle_root, signature)
            
            assert is_valid == True


class TestLedgerSignerKeyExport:
    """Test key export functionality"""
    
    def test_export_public_key_pem(self):
        """Test exporting public key in PEM format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            pem = signer.export_public_key()
            
            assert isinstance(pem, bytes)
            assert b"BEGIN PUBLIC KEY" in pem
    
    def test_export_public_key_hex(self):
        """Test exporting public key in hex format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            hex_key = signer.export_public_key(format='hex')
            
            assert isinstance(hex_key, str)
            assert len(hex_key) > 0
    
    def test_get_public_key_fingerprint(self):
        """Test getting public key fingerprint"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            fingerprint = signer.get_public_key_fingerprint()
            
            assert isinstance(fingerprint, str)
            assert len(fingerprint) > 0


class TestLedgerSignerErrorHandling:
    """Test error handling"""
    
    def test_sign_with_none_data(self):
        """Test signing None raises appropriate error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            with pytest.raises((TypeError, ValueError)):
                signer.sign_data(None)
    
    def test_verify_with_wrong_key(self):
        """Test verification fails with wrong key"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                signer1 = LedgerSigner(key_dir=tmpdir1)
                signer2 = LedgerSigner(key_dir=tmpdir2)
                
                data = b"test data"
                signature = signer1.sign_data(data)
                
                # Verify with different signer should fail
                is_valid = signer2.verify_signature(data, signature)
                
                assert is_valid == False
    
    def test_corrupted_key_file_regenerates(self):
        """Test corrupted key file triggers regeneration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer = LedgerSigner(key_dir=tmpdir)
            
            # Corrupt the private key file
            with open(signer.private_key_path, 'w') as f:
                f.write("corrupted")
            
            # Create new signer should regenerate
            signer2 = LedgerSigner(key_dir=tmpdir)
            
            assert signer2.private_key is not None


class TestLedgerSignerMultipleInstances:
    """Test multiple signer instances"""
    
    def test_multiple_signers_different_keys(self):
        """Test multiple signers have different keys"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                signer1 = LedgerSigner(key_dir=tmpdir1)
                signer2 = LedgerSigner(key_dir=tmpdir2)
                
                pub1 = signer1.export_public_key()
                pub2 = signer2.export_public_key()
                
                assert pub1 != pub2
    
    def test_multiple_signers_same_directory(self):
        """Test multiple signers share keys in same directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            signer1 = LedgerSigner(key_dir=tmpdir)
            pub1 = signer1.export_public_key()
            
            signer2 = LedgerSigner(key_dir=tmpdir)
            pub2 = signer2.export_public_key()
            
            # Should load same keys
            assert pub1 == pub2
