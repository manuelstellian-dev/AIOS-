"""
Secrets Vault Module for VENOM
Provides encrypted storage for secrets with master password protection
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class SecretsVault:
    """
    Encrypted secrets vault with master password protection
    
    Features:
    - Encrypt secrets at rest with Fernet
    - Master password with PBKDF2 key derivation
    - Environment variable injection
    - Backup and restore with re-encryption
    """
    
    def __init__(self, vault_file: str = 'secrets.vault', master_password: Optional[str] = None):
        """
        Initialize secrets vault
        
        Args:
            vault_file: Path to encrypted vault file
            master_password: Master password for encryption
        """
        self.vault_file = Path(vault_file)
        self.vault_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._secrets: Dict[str, str] = {}
        self._fernet: Optional[Fernet] = None
        self._salt: Optional[bytes] = None
        
        if master_password:
            self._initialize_encryption(master_password)
            self._load_vault()
        
        logger.info(f"Secrets vault initialized: {self.vault_file}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Master password
            salt: Salt for key derivation
            
        Returns:
            Derived key (32 bytes)
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def _initialize_encryption(self, password: str) -> None:
        """
        Initialize Fernet encryption with master password
        
        Args:
            password: Master password
        """
        # Load or generate salt
        if self.vault_file.exists():
            try:
                with open(self.vault_file, 'r') as f:
                    data = json.load(f)
                    self._salt = base64.b64decode(data['salt'])
            except Exception as e:
                logger.warning(f"Failed to load salt: {e}")
                self._salt = os.urandom(16)
        else:
            self._salt = os.urandom(16)
        
        # Derive key from password
        key = self._derive_key(password, self._salt)
        
        # Initialize Fernet
        fernet_key = base64.urlsafe_b64encode(key)
        self._fernet = Fernet(fernet_key)
    
    def _load_vault(self) -> None:
        """Load and decrypt vault from file"""
        if not self.vault_file.exists():
            logger.info("Vault file does not exist, starting fresh")
            return
        
        try:
            with open(self.vault_file, 'r') as f:
                data = json.load(f)
            
            # Decrypt secrets
            encrypted_secrets = data.get('secrets', {})
            
            for key, encrypted_value in encrypted_secrets.items():
                try:
                    decrypted = self._fernet.decrypt(encrypted_value.encode())
                    self._secrets[key] = decrypted.decode()
                except Exception:
                    logger.error("Failed to decrypt a secret")
            
            logger.info(f"Loaded {len(self._secrets)} secrets from vault")
        
        except Exception as e:
            logger.error(f"Failed to load vault: {e}")
            raise
    
    def _save_vault(self) -> None:
        """Encrypt and save vault to file"""
        if not self._fernet:
            raise RuntimeError("Vault not initialized with master password")
        
        # Encrypt secrets
        encrypted_secrets = {}
        
        for key, value in self._secrets.items():
            encrypted = self._fernet.encrypt(value.encode())
            encrypted_secrets[key] = encrypted.decode()
        
        # Save to file
        data = {
            'salt': base64.b64encode(self._salt).decode(),
            'secrets': encrypted_secrets
        }
        
        with open(self.vault_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved {len(self._secrets)} secrets to vault")
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Store a secret in the vault
        
        Args:
            key: Secret key/name
            value: Secret value
        """
        if not self._fernet:
            raise RuntimeError("Vault not initialized with master password")
        
        self._secrets[key] = value
        self._save_vault()
        
        logger.info(f"Secret '{key}' stored in vault")
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a secret from the vault
        
        Args:
            key: Secret key/name
            
        Returns:
            Secret value or None if not found
        """
        value = self._secrets.get(key)
        
        if value is None:
            logger.warning(f"Secret '{key}' not found in vault")
        
        return value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret from the vault
        
        Args:
            key: Secret key/name
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._secrets:
            del self._secrets[key]
            self._save_vault()
            logger.info(f"Secret '{key}' deleted from vault")
            return True
        
        logger.warning(f"Secret '{key}' not found in vault")
        return False
    
    def list_keys(self) -> List[str]:
        """
        List all secret keys in the vault
        
        Returns:
            List of secret keys
        """
        return list(self._secrets.keys())
    
    def rotate_master_key(self, new_password: str) -> None:
        """
        Rotate master encryption key (re-encrypt all secrets)
        
        Args:
            new_password: New master password
        """
        if not self._fernet:
            raise RuntimeError("Vault not initialized with master password")
        
        logger.info("Rotating master key...")
        
        # Keep secrets in memory
        secrets_copy = self._secrets.copy()
        
        # Generate new salt and key
        self._salt = os.urandom(16)
        key = self._derive_key(new_password, self._salt)
        fernet_key = base64.urlsafe_b64encode(key)
        self._fernet = Fernet(fernet_key)
        
        # Re-encrypt with new key
        self._secrets = secrets_copy
        self._save_vault()
        
        logger.info("Master key rotated successfully")
    
    def load_to_env(self, prefix: str = 'VENOM_') -> None:
        """
        Load secrets to environment variables
        
        Args:
            prefix: Prefix for environment variable names
        """
        for key, value in self._secrets.items():
            env_var = f"{prefix}{key.upper()}"
            os.environ[env_var] = value
        
        logger.info(f"Loaded {len(self._secrets)} secrets to environment")
    
    def backup(self, backup_path: str) -> None:
        """
        Backup vault to file
        
        Args:
            backup_path: Path for backup file
        """
        if not self.vault_file.exists():
            raise RuntimeError("No vault file to backup")
        
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy vault file
        import shutil
        shutil.copy2(self.vault_file, backup_file)
        
        logger.info(f"Vault backed up to {backup_path}")
    
    def restore(self, backup_path: str) -> None:
        """
        Restore vault from backup
        
        Args:
            backup_path: Path to backup file
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Copy backup to vault file
        import shutil
        shutil.copy2(backup_file, self.vault_file)
        
        # Reload vault
        self._secrets.clear()
        self._load_vault()
        
        logger.info(f"Vault restored from {backup_path}")
