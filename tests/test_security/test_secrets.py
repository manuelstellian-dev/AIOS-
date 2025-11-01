"""
Tests for Secrets Vault
"""
import pytest
import os
from venom.security.secrets import SecretsVault


def test_set_get_secret(tmp_path):
    """Test storing and retrieving secrets"""
    vault_file = tmp_path / "test.vault"
    vault = SecretsVault(str(vault_file), master_password="test-password")
    
    # Set secrets
    vault.set_secret("api_key", "secret-api-key-12345")
    vault.set_secret("db_password", "super-secret-password")
    
    # Get secrets
    assert vault.get_secret("api_key") == "secret-api-key-12345"
    assert vault.get_secret("db_password") == "super-secret-password"
    
    # Get non-existent secret
    assert vault.get_secret("non_existent") is None
    
    # List keys
    keys = vault.list_keys()
    assert len(keys) == 2
    assert "api_key" in keys
    assert "db_password" in keys
    
    # Verify vault file was created and encrypted
    assert vault_file.exists()


def test_delete_secret(tmp_path):
    """Test deleting secrets from vault"""
    vault_file = tmp_path / "test.vault"
    vault = SecretsVault(str(vault_file), master_password="test-password")
    
    # Set secrets
    vault.set_secret("temp_secret", "temporary-value")
    vault.set_secret("keep_secret", "permanent-value")
    
    # Verify both exist
    assert vault.get_secret("temp_secret") == "temporary-value"
    assert vault.get_secret("keep_secret") == "permanent-value"
    
    # Delete one secret
    assert vault.delete_secret("temp_secret")
    
    # Verify deletion
    assert vault.get_secret("temp_secret") is None
    assert vault.get_secret("keep_secret") == "permanent-value"
    
    # Try to delete non-existent secret
    assert not vault.delete_secret("non_existent")


def test_rotate_master_key(tmp_path):
    """Test rotating master encryption key"""
    vault_file = tmp_path / "test.vault"
    vault = SecretsVault(str(vault_file), master_password="old-password")
    
    # Set secrets
    vault.set_secret("secret1", "value1")
    vault.set_secret("secret2", "value2")
    
    # Rotate master key
    vault.rotate_master_key("new-password")
    
    # Verify secrets are still accessible
    assert vault.get_secret("secret1") == "value1"
    assert vault.get_secret("secret2") == "value2"
    
    # Create new vault with new password
    vault2 = SecretsVault(str(vault_file), master_password="new-password")
    
    # Verify secrets can be loaded with new password
    assert vault2.get_secret("secret1") == "value1"
    assert vault2.get_secret("secret2") == "value2"


def test_backup_restore(tmp_path):
    """Test backup and restore functionality"""
    vault_file = tmp_path / "test.vault"
    backup_file = tmp_path / "backup.vault"
    
    # Create vault with secrets
    vault = SecretsVault(str(vault_file), master_password="test-password")
    vault.set_secret("secret1", "value1")
    vault.set_secret("secret2", "value2")
    
    # Backup vault
    vault.backup(str(backup_file))
    assert backup_file.exists()
    
    # Delete a secret from original vault
    vault.delete_secret("secret1")
    assert vault.get_secret("secret1") is None
    
    # Restore from backup
    vault.restore(str(backup_file))
    
    # Verify secret was restored
    assert vault.get_secret("secret1") == "value1"
    assert vault.get_secret("secret2") == "value2"


def test_persistence(tmp_path):
    """Test that secrets persist across vault instances"""
    vault_file = tmp_path / "test.vault"
    
    # Create vault and store secrets
    vault1 = SecretsVault(str(vault_file), master_password="test-password")
    vault1.set_secret("persistent_key", "persistent_value")
    
    # Create new vault instance with same file and password
    vault2 = SecretsVault(str(vault_file), master_password="test-password")
    
    # Verify secret persists
    assert vault2.get_secret("persistent_key") == "persistent_value"


def test_load_to_env(tmp_path):
    """Test loading secrets to environment variables"""
    vault_file = tmp_path / "test.vault"
    vault = SecretsVault(str(vault_file), master_password="test-password")
    
    # Set secrets
    vault.set_secret("api_key", "test-api-key")
    vault.set_secret("db_host", "localhost")
    
    # Load to environment
    vault.load_to_env(prefix="TEST_")
    
    # Verify environment variables
    assert os.environ.get("TEST_API_KEY") == "test-api-key"
    assert os.environ.get("TEST_DB_HOST") == "localhost"
    
    # Clean up environment
    del os.environ["TEST_API_KEY"]
    del os.environ["TEST_DB_HOST"]
