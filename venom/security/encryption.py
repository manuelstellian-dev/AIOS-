"""
Advanced Encryption Module for VENOM
Provides AES-256-GCM, RSA, and Fernet encryption with digital signatures
"""
import os
import logging
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

logger = logging.getLogger(__name__)


class AdvancedEncryption:
    """
    Advanced encryption supporting multiple algorithms
    
    Algorithms:
    - aes-gcm: AES-256-GCM (authenticated encryption)
    - rsa: RSA with OAEP padding
    - fernet: Symmetric encryption with Fernet
    
    Features:
    - Key generation
    - Symmetric/asymmetric encryption
    - Digital signatures (Ed25519)
    - Key derivation (PBKDF2)
    """
    
    # Supported encryption algorithms
    SUPPORTED_ALGORITHMS = ['aes-gcm', 'rsa', 'fernet']
    
    def __init__(self, algorithm: str = 'aes-gcm'):
        """
        Initialize encryption engine
        
        Args:
            algorithm: Encryption algorithm ('aes-gcm', 'rsa', 'fernet')
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        self.algorithm = algorithm
        logger.info(f"Encryption engine initialized with {algorithm}")
    
    @staticmethod
    def generate_key(algorithm: str = 'fernet') -> bytes:
        """
        Generate a symmetric encryption key
        
        For AES-GCM: 256-bit key (raw bytes)
        For Fernet: URL-safe base64-encoded 32-byte key
        
        Args:
            algorithm: Algorithm to generate key for ('aes-gcm' or 'fernet')
        
        Returns:
            Encryption key bytes
        """
        if algorithm == 'aes-gcm':
            # Generate 256-bit (32-byte) raw key for AES-256-GCM
            return os.urandom(32)
        else:
            # Generate Fernet key (base64-encoded 32-byte key)
            return Fernet.generate_key()
    
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """
        Encrypt data with symmetric encryption
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Encrypted data (includes nonce/IV for AES-GCM)
        """
        if self.algorithm == 'aes-gcm':
            # AES-256-GCM encryption
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)  # 96-bit nonce
            ciphertext = aesgcm.encrypt(nonce, data, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        
        elif self.algorithm == 'fernet':
            # Fernet encryption
            f = Fernet(key)
            return f.encrypt(data)
        
        else:
            raise ValueError(f"Symmetric encryption not supported for {self.algorithm}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data with symmetric encryption
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            
        Returns:
            Decrypted data
        """
        if self.algorithm == 'aes-gcm':
            # AES-256-GCM decryption
            aesgcm = AESGCM(key)
            # Extract nonce and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            return aesgcm.decrypt(nonce, ciphertext, None)
        
        elif self.algorithm == 'fernet':
            # Fernet decryption
            f = Fernet(key)
            return f.decrypt(encrypted_data)
        
        else:
            raise ValueError(f"Symmetric decryption not supported for {self.algorithm}")
    
    @staticmethod
    def generate_keypair(key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA keypair
        
        Args:
            key_size: Key size in bits (default: 2048)
            
        Returns:
            Tuple of (private_key, public_key) as PEM bytes
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return (private_pem, public_pem)
    
    @staticmethod
    def encrypt_asymmetric(data: bytes, public_key: bytes) -> bytes:
        """
        Encrypt data with RSA public key
        
        Args:
            data: Data to encrypt
            public_key: RSA public key (PEM format)
            
        Returns:
            Encrypted data
        """
        # Load public key
        public_key_obj = serialization.load_pem_public_key(
            public_key,
            backend=default_backend()
        )
        
        # Encrypt with OAEP padding
        ciphertext = public_key_obj.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return ciphertext
    
    @staticmethod
    def decrypt_asymmetric(encrypted_data: bytes, private_key: bytes) -> bytes:
        """
        Decrypt data with RSA private key
        
        Args:
            encrypted_data: Encrypted data
            private_key: RSA private key (PEM format)
            
        Returns:
            Decrypted data
        """
        # Load private key
        private_key_obj = serialization.load_pem_private_key(
            private_key,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt with OAEP padding
        plaintext = private_key_obj.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext
    
    @staticmethod
    def sign(data: bytes, private_key: bytes) -> bytes:
        """
        Sign data with Ed25519 private key
        
        Args:
            data: Data to sign
            private_key: Ed25519 private key (PEM format)
            
        Returns:
            Signature bytes
        """
        # Load private key
        private_key_obj = serialization.load_pem_private_key(
            private_key,
            password=None,
            backend=default_backend()
        )
        
        # Sign data
        signature = private_key_obj.sign(data)
        return signature
    
    @staticmethod
    def verify(data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify Ed25519 signature
        
        Args:
            data: Original data
            signature: Signature to verify
            public_key: Ed25519 public key (PEM format)
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Load public key
            public_key_obj = serialization.load_pem_public_key(
                public_key,
                backend=default_backend()
            )
            
            # Verify signature
            public_key_obj.verify(signature, data)
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def derive_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password string
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        # Generate salt if not provided
        if salt is None:
            salt = os.urandom(16)
        
        # Derive key using PBKDF2-HMAC-SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=salt,
            iterations=100000,  # 100k iterations
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return (key, salt)
    
    @staticmethod
    def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
        """
        Generate Ed25519 keypair for signatures
        
        Returns:
            Tuple of (private_key, public_key) as PEM bytes
        """
        # Generate private key
        private_key = Ed25519PrivateKey.generate()
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return (private_pem, public_pem)
