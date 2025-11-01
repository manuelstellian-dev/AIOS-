"""
Tests for Advanced Encryption Module
"""
import pytest
from venom.security.encryption import AdvancedEncryption


def test_aes_gcm_encryption():
    """Test AES-256-GCM encryption and decryption"""
    enc = AdvancedEncryption('aes-gcm')
    
    # Generate key for AES-GCM
    key = AdvancedEncryption.generate_key('aes-gcm')
    assert len(key) == 32  # 256-bit key
    
    # Test data
    plaintext = b"Secret message for AES-GCM"
    
    # Encrypt
    ciphertext = enc.encrypt(plaintext, key)
    assert ciphertext != plaintext
    assert len(ciphertext) > len(plaintext)  # Includes nonce
    
    # Decrypt
    decrypted = enc.decrypt(ciphertext, key)
    assert decrypted == plaintext


def test_rsa_encryption():
    """Test RSA asymmetric encryption and decryption"""
    # Generate keypair
    private_key, public_key = AdvancedEncryption.generate_keypair(2048)
    assert b'BEGIN PRIVATE KEY' in private_key
    assert b'BEGIN PUBLIC KEY' in public_key
    
    # Test data
    plaintext = b"Secret message for RSA"
    
    # Encrypt with public key
    ciphertext = AdvancedEncryption.encrypt_asymmetric(plaintext, public_key)
    assert ciphertext != plaintext
    
    # Decrypt with private key
    decrypted = AdvancedEncryption.decrypt_asymmetric(ciphertext, private_key)
    assert decrypted == plaintext


def test_fernet_encryption():
    """Test Fernet symmetric encryption and decryption"""
    enc = AdvancedEncryption('fernet')
    
    # Generate key for Fernet
    key = AdvancedEncryption.generate_key('fernet')
    
    # Test data
    plaintext = b"Secret message for Fernet"
    
    # Encrypt
    ciphertext = enc.encrypt(plaintext, key)
    assert ciphertext != plaintext
    
    # Decrypt
    decrypted = enc.decrypt(ciphertext, key)
    assert decrypted == plaintext


def test_digital_signatures():
    """Test Ed25519 digital signatures"""
    # Generate Ed25519 keypair
    private_key, public_key = AdvancedEncryption.generate_ed25519_keypair()
    assert b'BEGIN PRIVATE KEY' in private_key
    assert b'BEGIN PUBLIC KEY' in public_key
    
    # Test data
    data = b"Message to sign"
    
    # Sign
    signature = AdvancedEncryption.sign(data, private_key)
    assert len(signature) == 64  # Ed25519 signature is 64 bytes
    
    # Verify valid signature
    assert AdvancedEncryption.verify(data, signature, public_key)
    
    # Verify invalid signature
    tampered_data = b"Tampered message"
    assert not AdvancedEncryption.verify(tampered_data, signature, public_key)


def test_key_derivation():
    """Test PBKDF2 key derivation from password"""
    password = "my-secure-password"
    
    # Derive key without salt
    key1, salt1 = AdvancedEncryption.derive_key(password)
    assert len(key1) == 32  # 256-bit key
    assert len(salt1) == 16  # Salt is 16 bytes
    
    # Derive key with same salt should produce same key
    key2, salt2 = AdvancedEncryption.derive_key(password, salt1)
    assert key1 == key2
    assert salt1 == salt2
    
    # Different password should produce different key
    key3, salt3 = AdvancedEncryption.derive_key("different-password", salt1)
    assert key3 != key1


def test_encrypt_decrypt_roundtrip():
    """Test complete encryption/decryption roundtrip for all algorithms"""
    test_data = b"This is a test message that will be encrypted and decrypted"
    
    # Test AES-GCM
    enc_aes = AdvancedEncryption('aes-gcm')
    key_aes = AdvancedEncryption.generate_key('aes-gcm')
    encrypted_aes = enc_aes.encrypt(test_data, key_aes)
    decrypted_aes = enc_aes.decrypt(encrypted_aes, key_aes)
    assert decrypted_aes == test_data
    
    # Test Fernet
    enc_fernet = AdvancedEncryption('fernet')
    key_fernet = AdvancedEncryption.generate_key('fernet')
    encrypted_fernet = enc_fernet.encrypt(test_data, key_fernet)
    decrypted_fernet = enc_fernet.decrypt(encrypted_fernet, key_fernet)
    assert decrypted_fernet == test_data
    
    # Test RSA
    private_key, public_key = AdvancedEncryption.generate_keypair(2048)
    encrypted_rsa = AdvancedEncryption.encrypt_asymmetric(test_data, public_key)
    decrypted_rsa = AdvancedEncryption.decrypt_asymmetric(encrypted_rsa, private_key)
    assert decrypted_rsa == test_data
