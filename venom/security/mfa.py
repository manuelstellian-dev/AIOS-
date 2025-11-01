"""
Multi-Factor Authentication Module for VENOM
Provides TOTP and backup codes for 2FA
"""
import pyotp
import qrcode
import secrets
import string
import logging
import bcrypt
from typing import List

logger = logging.getLogger(__name__)


class MFAManager:
    """
    Multi-factor authentication manager
    
    Features:
    - TOTP (Time-based One-Time Password)
    - Backup codes generation and verification
    - QR code generation for authenticator apps
    - Secure code hashing with bcrypt
    """
    
    def __init__(self):
        """Initialize MFA manager"""
        logger.info("MFA manager initialized")
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random secret for TOTP
        
        Returns:
            Base32-encoded secret string
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_provisioning_uri(secret: str, username: str, issuer: str = 'VENOM') -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            secret: TOTP secret
            username: Username/email
            issuer: Service name (default: VENOM)
            
        Returns:
            Provisioning URI for QR code
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: TOTP secret
            token: 6-digit token from authenticator app
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            # Verify with time drift tolerance (±1 period = ±30s)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.warning(f"TOTP verification failed: {e}")
            return False
    
    @staticmethod
    def get_current_totp(secret: str) -> str:
        """
        Get current TOTP code
        
        Args:
            secret: TOTP secret
            
        Returns:
            Current 6-digit TOTP code
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes
        
        Args:
            count: Number of backup codes to generate (default: 10)
            
        Returns:
            List of 8-character alphanumeric backup codes
            
        Note:
            Uses uppercase letters and digits (36 characters) for better
            readability and user experience. This provides sufficient entropy
            (8 chars from 36 = ~41 bits) for backup codes.
        """
        codes = []
        alphabet = string.ascii_uppercase + string.digits
        
        for _ in range(count):
            # Generate 8-character code
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            codes.append(code)
        
        logger.info(f"Generated {count} backup codes")
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash backup code with bcrypt
        
        Args:
            code: Backup code to hash
            
        Returns:
            Hashed code (bcrypt hash string)
        """
        # Hash with bcrypt (includes salt)
        hashed = bcrypt.hashpw(code.encode(), bcrypt.gensalt())
        return hashed.decode()
    
    @staticmethod
    def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
        """
        Verify backup code against hashed codes
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
            
        Returns:
            True if code matches any hashed code, False otherwise
        """
        for hashed in hashed_codes:
            try:
                if bcrypt.checkpw(code.encode(), hashed.encode()):
                    logger.info("Backup code verified successfully")
                    return True
            except Exception as e:
                logger.warning(f"Backup code verification error: {e}")
                continue
        
        logger.warning("Backup code verification failed")
        return False
    
    @staticmethod
    def generate_qr_code(provisioning_uri: str, output_path: str) -> None:
        """
        Generate QR code image for TOTP provisioning
        
        Args:
            provisioning_uri: Provisioning URI from get_provisioning_uri()
            output_path: Path to save QR code image
        """
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            
            logger.info(f"QR code saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            raise
