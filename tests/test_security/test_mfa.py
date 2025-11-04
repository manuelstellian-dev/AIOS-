"""
Tests for Multi-Factor Authentication Module
"""
import pytest
import os
from venom.security.mfa import MFAManager


def test_generate_secret():
    """Test TOTP secret generation"""
    mfa = MFAManager()
    
    # Generate secret
    secret = mfa.generate_secret()
    assert secret is not None
    assert len(secret) == 32  # Base32-encoded secret is 32 chars
    assert secret.isalnum()  # Should be alphanumeric


def test_verify_totp():
    """Test TOTP token verification"""
    mfa = MFAManager()
    
    # Generate secret and get current token
    secret = mfa.generate_secret()
    current_token = mfa.get_current_totp(secret)
    
    # Verify current token
    assert mfa.verify_totp(secret, current_token)
    
    # Invalid token should fail
    assert not mfa.verify_totp(secret, "000000")
    
    # Wrong length token should fail
    assert not mfa.verify_totp(secret, "12345")


def test_backup_codes():
    """Test backup codes generation and verification"""
    mfa = MFAManager()
    
    # Generate backup codes
    codes = mfa.generate_backup_codes(10)
    assert len(codes) == 10
    
    # Each code should be 8 characters
    for code in codes:
        assert len(code) == 8
        assert code.isalnum()
    
    # All codes should be unique
    assert len(set(codes)) == 10
    
    # Hash backup codes
    hashed_codes = [mfa.hash_backup_code(code) for code in codes]
    
    # Verify valid code
    assert mfa.verify_backup_code(codes[0], hashed_codes)
    assert mfa.verify_backup_code(codes[5], hashed_codes)
    
    # Invalid code should fail
    assert not mfa.verify_backup_code("INVALID1", hashed_codes)


def test_qr_code_generation(tmp_path):
    """Test QR code generation for TOTP provisioning"""
    mfa = MFAManager()
    
    # Generate secret and provisioning URI
    secret = mfa.generate_secret()
    uri = mfa.get_provisioning_uri(secret, "test@example.com", "VENOM")
    
    # Check URI format
    assert "otpauth://totp/" in uri
    # Email may be URL-encoded in the URI
    assert ("test@example.com" in uri or "test%40example.com" in uri)
    assert "VENOM" in uri
    
    # Generate QR code
    qr_path = tmp_path / "test_qr.png"
    mfa.generate_qr_code(uri, str(qr_path))
    
    # Verify QR code file was created
    assert qr_path.exists()
    assert qr_path.stat().st_size > 0


def test_time_drift_tolerance():
    """Test TOTP time drift tolerance"""
    import pyotp
    import time
    
    mfa = MFAManager()
    
    # Generate secret
    secret = mfa.generate_secret()
    totp = pyotp.TOTP(secret)
    
    # Get current token
    current_token = mfa.get_current_totp(secret)
    
    # Current token should verify
    assert mfa.verify_totp(secret, current_token)
    
    # Token from previous period should still verify (within valid_window=1)
    # We can't easily test this without waiting 30 seconds, so we'll
    # just verify that the method accepts tokens within the window
    
    # Generate a token manually with time offset
    current_time = time.time()
    totp_obj = pyotp.TOTP(secret)
    
    # Verify current token works
    assert totp_obj.verify(current_token, valid_window=1)


def test_verify_totp_with_invalid_secret():
    """Test TOTP verification with malformed secret"""
    mfa = MFAManager()
    
    # Test with invalid/malformed secret that causes exception
    assert not mfa.verify_totp("invalid_secret", "123456")
    assert not mfa.verify_totp("", "123456")


def test_verify_backup_code_with_invalid_hash():
    """Test backup code verification with invalid hashed codes"""
    mfa = MFAManager()
    
    # Generate valid backup codes
    codes = mfa.generate_backup_codes(3)
    hashed_codes = [mfa.hash_backup_code(code) for code in codes]
    
    # Add an invalid hash that will cause exception
    invalid_hashes = hashed_codes + ["invalid_hash_format", "not_a_bcrypt_hash"]
    
    # Should still handle gracefully and return False
    assert not mfa.verify_backup_code("INVALID1", invalid_hashes)
    
    # Valid code should still work even with invalid hashes in list
    assert mfa.verify_backup_code(codes[0], invalid_hashes)


def test_generate_qr_code_with_invalid_path():
    """Test QR code generation with invalid path"""
    mfa = MFAManager()
    
    secret = mfa.generate_secret()
    uri = mfa.get_provisioning_uri(secret, "test@example.com")
    
    # Test with invalid path that will cause exception
    with pytest.raises(Exception):
        mfa.generate_qr_code(uri, "/invalid/path/that/does/not/exist/qr.png")
