# Security Module

The Security module provides comprehensive cryptography and authentication features.

## Components

### Advanced Encryption

Multiple encryption algorithms for different use cases.

```python
from venom.security import AdvancedEncryption

# AES-GCM (recommended for most cases)
encryption = AdvancedEncryption(algorithm='aes-gcm')
key = encryption.generate_key()
encrypted, nonce = encryption.encrypt(b"sensitive data", key)
decrypted = encryption.decrypt(encrypted, key, nonce)

# RSA (for asymmetric encryption)
encryption = AdvancedEncryption(algorithm='rsa')
public_key, private_key = encryption.generate_keypair()
encrypted = encryption.encrypt_with_public_key(b"data", public_key)
decrypted = encryption.decrypt_with_private_key(encrypted, private_key)

# Fernet (simple symmetric encryption)
encryption = AdvancedEncryption(algorithm='fernet')
key = encryption.generate_key()
encrypted = encryption.encrypt_fernet(b"data", key)
decrypted = encryption.decrypt_fernet(encrypted, key)
```

### Ledger Signing

Ed25519 digital signatures for data integrity.

```python
from venom.security import LedgerSigner

# Initialize signer
signer = LedgerSigner()

# Sign data
data = {"transaction": "transfer", "amount": 100}
signature = signer.sign_entry(data)

# Verify signature
is_valid = signer.verify_signature(data, signature)
```

### Multi-Factor Authentication (MFA)

TOTP-based two-factor authentication.

```python
from venom.security import MFA

# Initialize MFA
mfa = MFA(issuer="VENOM")

# Generate secret for user
secret = mfa.generate_secret()

# Get QR code for user to scan
qr_code = mfa.get_qr_code(secret, username="user@example.com")

# Verify OTP token
token = "123456"  # From user's authenticator app
is_valid = mfa.verify_token(secret, token)

# Generate backup codes
backup_codes = mfa.generate_backup_codes()
```

### Secrets Manager

Encrypted storage for sensitive configuration.

```python
from venom.security import SecretsManager

# Initialize secrets manager
secrets = SecretsManager(storage_path="~/.venom/secrets")

# Store secret
secrets.set_secret("api_key", "sk-1234567890")
secrets.set_secret("db_password", "secure_password")

# Retrieve secret
api_key = secrets.get_secret("api_key")

# List all secrets
all_secrets = secrets.list_secrets()

# Delete secret
secrets.delete_secret("api_key")

# Rotate encryption key
secrets.rotate_key()
```

## CLI Usage

```bash
# Encrypt a file
venom security encrypt --file sensitive.txt

# Scan for security issues
venom security scan --path ./src

# The encrypted file and key will be created:
# - sensitive.txt.encrypted
# - sensitive.txt.key
```

## Security Best Practices

### 1. Key Management

```python
# ✓ GOOD: Store keys separately
encryption = AdvancedEncryption(algorithm='aes-gcm')
key = encryption.generate_key()

# Save key securely (not in source code!)
with open('/secure/location/key.bin', 'wb') as f:
    f.write(key)

# ✗ BAD: Hardcode keys
key = b'hardcoded_key_in_source'  # Never do this!
```

### 2. Use Strong Algorithms

```python
# ✓ GOOD: Use AES-GCM (authenticated encryption)
encryption = AdvancedEncryption(algorithm='aes-gcm')

# ✗ AVOID: Using deprecated algorithms
# (VENOM only provides secure algorithms)
```

### 3. Verify Signatures

```python
# ✓ GOOD: Always verify signatures
signer = LedgerSigner()
signature = signer.sign_entry(data)

# Later, verify before using
if signer.verify_signature(data, signature):
    # Process data
    pass
else:
    raise SecurityError("Invalid signature")
```

### 4. Secure Secret Storage

```python
# ✓ GOOD: Use SecretsManager
secrets = SecretsManager()
secrets.set_secret("api_key", api_key)

# ✗ BAD: Store in plain text
with open('config.txt', 'w') as f:
    f.write(f"API_KEY={api_key}")  # Never do this!
```

## Configuration

Add to `~/.venomrc`:

```json
{
  "security": {
    "enable_encryption": true,
    "enable_signing": true,
    "default_algorithm": "aes-gcm",
    "mfa": {
      "enabled": true,
      "issuer": "VENOM"
    },
    "secrets": {
      "storage_path": "~/.venom/secrets",
      "auto_rotate_days": 90
    }
  }
}
```

## File Encryption Example

```bash
# Encrypt a configuration file
venom security encrypt --file config.json

# This creates:
# - config.json.encrypted (encrypted data)
# - config.json.key (encryption key)

# To decrypt programmatically:
```

```python
from venom.security import AdvancedEncryption

encryption = AdvancedEncryption(algorithm='aes-gcm')

# Read key
with open('config.json.key', 'rb') as f:
    key = f.read()

# Read encrypted data (nonce + ciphertext)
with open('config.json.encrypted', 'rb') as f:
    data = f.read()
    nonce = data[:12]  # First 12 bytes
    ciphertext = data[12:]  # Rest is ciphertext

# Decrypt
plaintext = encryption.decrypt(ciphertext, key, nonce)

# Use the decrypted data
import json
config = json.loads(plaintext)
```

## Compliance

The Security module helps with:

- **GDPR**: Encryption at rest and in transit
- **HIPAA**: Secure handling of sensitive data
- **PCI DSS**: Strong cryptography for payment data
- **SOC 2**: Audit trails and access logging

## Examples

See [examples/security/](../examples/) for complete examples.

## API Reference

Full API documentation available at [docs/api/security.md](../api/security.md).
