"""
Ledger Signing Module using Ed25519
Signs ledger entries and Merkle root for attestation
"""
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)


class LedgerSigner:
    """
    Signs ledger entries and Merkle root using Ed25519
    
    Features:
    - Generate Ed25519 keypair
    - Store keys securely
    - Sign ledger entries
    - Sign Merkle root for attestation
    - Verify signatures
    """
    
    def __init__(self, key_dir: str = ".venom/keys"):
        """
        Initialize ledger signer
        
        Args:
            key_dir: Directory for key storage
        """
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        
        self.private_key_path = self.key_dir / "ledger_private.pem"
        self.public_key_path = self.key_dir / "ledger_public.pem"
        
        self.private_key: Optional[Ed25519PrivateKey] = None
        self.public_key: Optional[Ed25519PublicKey] = None
        
        # Load or generate keys
        self._load_or_generate_keys()
    
    def _load_or_generate_keys(self):
        """Load existing keys or generate new keypair"""
        if self.private_key_path.exists() and self.public_key_path.exists():
            # Load existing keys
            try:
                with open(self.private_key_path, 'rb') as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                
                with open(self.public_key_path, 'rb') as f:
                    self.public_key = serialization.load_pem_public_key(f.read())
                
                logger.info(f"Loaded Ed25519 keys from {self.key_dir}")
            except Exception as e:
                logger.error(f"Failed to load keys: {e}")
                self._generate_keys()
        else:
            # Generate new keys
            self._generate_keys()
    
    def _generate_keys(self):
        """Generate new Ed25519 keypair"""
        logger.info("Generating new Ed25519 keypair...")
        
        # Generate private key
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        # Save private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(self.private_key_path, 'wb') as f:
            f.write(private_pem)
        
        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(self.public_key_path, 'wb') as f:
            f.write(public_pem)
        
        # Set restrictive permissions
        os.chmod(self.private_key_path, 0o600)
        os.chmod(self.public_key_path, 0o644)
        
        logger.info(f"Keys saved to {self.key_dir}")
    
    def sign_entry(self, entry_data: Dict[str, Any]) -> bytes:
        """
        Sign a ledger entry
        
        Args:
            entry_data: Entry data to sign
            
        Returns:
            Signature bytes
        """
        if not self.private_key:
            raise RuntimeError("Private key not loaded")
        
        # Create canonical representation
        entry_json = json.dumps(entry_data, sort_keys=True, separators=(",", ":"))
        
        # Sign
        signature = self.private_key.sign(entry_json.encode())
        return signature
    
    def sign_merkle_root(self, merkle_root: str) -> bytes:
        """
        Sign Merkle root for attestation
        
        Args:
            merkle_root: Merkle root hash
            
        Returns:
            Signature bytes
        """
        if not self.private_key:
            raise RuntimeError("Private key not loaded")
        
        signature = self.private_key.sign(merkle_root.encode())
        return signature
    
    def verify_entry(self, entry_data: Dict[str, Any], signature: bytes) -> bool:
        """
        Verify ledger entry signature
        
        Args:
            entry_data: Entry data
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        try:
            entry_json = json.dumps(entry_data, sort_keys=True, separators=(",", ":"))
            self.public_key.verify(signature, entry_json.encode())
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    def verify_merkle_root(self, merkle_root: str, signature: bytes) -> bool:
        """
        Verify Merkle root signature
        
        Args:
            merkle_root: Merkle root hash
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        try:
            self.public_key.verify(signature, merkle_root.encode())
            return True
        except Exception as e:
            logger.warning(f"Merkle root signature verification failed: {e}")
            return False
    
    def get_public_key_hex(self) -> str:
        """
        Get public key as hex string
        
        Returns:
            Public key hex string
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return public_bytes.hex()
    
    # Alias methods for backward compatibility
    def sign_data(self, data: Any) -> bytes:
        """
        Sign arbitrary data (alias for sign_entry for compatibility)
        
        Args:
            data: Data to sign (bytes, str, or dict)
            
        Returns:
            Signature bytes
        """
        if not self.private_key:
            raise RuntimeError("Private key not loaded")
        
        # Check for None
        if data is None:
            raise ValueError("Cannot sign None data")
        
        # Convert data to bytes
        if isinstance(data, bytes):
            data_bytes = data
        elif isinstance(data, str):
            data_bytes = data.encode()
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        else:
            data_bytes = str(data).encode()
        
        signature = self.private_key.sign(data_bytes)
        return signature
    
    def sign_ledger_entry(self, entry_data: Dict[str, Any]) -> bytes:
        """Alias for sign_entry for backward compatibility"""
        return self.sign_entry(entry_data)
    
    def verify_signature(self, data: Any, signature: bytes) -> bool:
        """
        Verify signature on arbitrary data (alias for verify_entry for compatibility)
        
        Args:
            data: Data that was signed
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        try:
            # Convert data to bytes
            if isinstance(data, bytes):
                data_bytes = data
            elif isinstance(data, str):
                data_bytes = data.encode()
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            else:
                data_bytes = str(data).encode()
            
            self.public_key.verify(signature, data_bytes)
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    def verify_ledger_entry(self, entry_data: Dict[str, Any], signature: bytes) -> bool:
        """Alias for verify_entry for backward compatibility"""
        return self.verify_entry(entry_data, signature)
    
    def export_public_key(self, format: str = 'pem'):
        """
        Export public key in various formats
        
        Args:
            format: Format ('pem' or 'hex')
            
        Returns:
            Public key as bytes (pem) or string (hex)
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        if format == 'hex':
            return self.get_public_key_hex()
        else:  # default to pem - return bytes
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return public_pem
    
    def get_public_key_fingerprint(self) -> str:
        """
        Get public key fingerprint (SHA256 hash of public key)
        
        Returns:
            Fingerprint hex string
        """
        if not self.public_key:
            raise RuntimeError("Public key not loaded")
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        fingerprint = hashlib.sha256(public_bytes).hexdigest()
        return fingerprint
