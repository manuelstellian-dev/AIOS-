#!/usr/bin/env python3
"""
Tests for VENOM CLI configuration management
Tests configuration file loading, validation, and default settings
"""
import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from venom.cli.main import VenomCLI


class TestConfigLoading:
    """Test configuration file loading"""
    
    def test_load_config_no_file(self):
        """Test loading config when no config file exists"""
        with patch.object(Path, 'exists', return_value=False):
            cli = VenomCLI()
            
            assert cli.config == {}
    
    def test_load_config_valid_file(self):
        """Test loading config from valid config file"""
        config_data = {
            "default_provider": "aws",
            "default_region": "us-east-1",
            "verbose": True
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                
                assert cli.config == config_data
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            with open(config_file, 'w') as f:
                f.write("{ invalid json }")
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                
                # Should return empty dict on invalid JSON
                assert cli.config == {}
    
    def test_load_config_empty_file(self):
        """Test loading config from empty file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            with open(config_file, 'w') as f:
                f.write("")
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                
                # Should return empty dict on empty file
                assert cli.config == {}


class TestConfigSaving:
    """Test configuration file saving"""
    
    def test_save_config_success(self):
        """Test saving config successfully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                cli.config = {
                    "default_provider": "aws",
                    "default_region": "us-west-2"
                }
                
                cli._save_config()
                
                # Verify file was created and contains correct data
                assert config_file.exists()
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                assert saved_config == cli.config
    
    def test_save_config_with_complex_data(self):
        """Test saving config with complex nested data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                cli.config = {
                    "providers": {
                        "aws": {"region": "us-east-1", "enabled": True},
                        "gcp": {"region": "us-central1", "enabled": False}
                    },
                    "settings": {
                        "verbose": True,
                        "timeout": 300
                    }
                }
                
                cli._save_config()
                
                # Verify file was created and contains correct data
                assert config_file.exists()
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                assert saved_config == cli.config
    
    def test_save_config_permission_error(self):
        """Test saving config when permissions are denied"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            # Create file with no write permissions
            config_file.touch()
            os.chmod(config_file, 0o444)  # Read-only
            
            try:
                with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                    cli = VenomCLI()
                    cli.config = {"test": "data"}
                    
                    # Should handle permission error gracefully
                    cli._save_config()
            finally:
                # Restore permissions for cleanup
                os.chmod(config_file, 0o644)


class TestDefaultConfig:
    """Test default configuration settings"""
    
    def test_default_version(self):
        """Test default VERSION constant"""
        assert VenomCLI.VERSION == "1.0.0"
    
    def test_default_config_file_location(self):
        """Test default config file location"""
        expected_path = Path.home() / ".venomrc"
        assert VenomCLI.CONFIG_FILE == expected_path
    
    def test_empty_config_on_init(self):
        """Test that empty config is created when no file exists"""
        with patch.object(Path, 'exists', return_value=False):
            cli = VenomCLI()
            
            assert isinstance(cli.config, dict)
            assert len(cli.config) == 0


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_config_is_dict(self):
        """Test that config is always a dictionary"""
        cli = VenomCLI()
        
        assert isinstance(cli.config, dict)
    
    def test_config_persists_across_operations(self):
        """Test that config persists across CLI operations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                # Create and save config
                cli1 = VenomCLI()
                cli1.config = {"test_key": "test_value"}
                cli1._save_config()
                
                # Load config in new CLI instance
                cli2 = VenomCLI()
                
                assert cli2.config == {"test_key": "test_value"}
    
    def test_config_update(self):
        """Test updating config values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                cli.config = {"key1": "value1"}
                cli._save_config()
                
                # Update config
                cli.config["key2"] = "value2"
                cli._save_config()
                
                # Load and verify
                cli2 = VenomCLI()
                assert cli2.config == {"key1": "value1", "key2": "value2"}


class TestConfigEdgeCases:
    """Test edge cases in config handling"""
    
    def test_config_with_unicode(self):
        """Test config with unicode characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                cli.config = {
                    "name": "测试",
                    "emoji": "🚀",
                    "special": "café"
                }
                cli._save_config()
                
                # Load and verify
                cli2 = VenomCLI()
                assert cli2.config == cli.config
    
    def test_config_with_special_types(self):
        """Test config with various data types"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".venomrc"
            
            with patch.object(VenomCLI, 'CONFIG_FILE', config_file):
                cli = VenomCLI()
                cli.config = {
                    "string": "value",
                    "integer": 42,
                    "float": 3.14,
                    "boolean": True,
                    "null": None,
                    "list": [1, 2, 3],
                    "nested": {"key": "value"}
                }
                cli._save_config()
                
                # Load and verify
                cli2 = VenomCLI()
                assert cli2.config == cli.config
    
    def test_config_file_path_expansion(self):
        """Test that config file path expands home directory"""
        # CONFIG_FILE should be an absolute path
        assert VenomCLI.CONFIG_FILE.is_absolute()
    
    def test_multiple_cli_instances(self):
        """Test that multiple CLI instances can coexist"""
        cli1 = VenomCLI()
        cli2 = VenomCLI()
        
        # Both should be independent instances
        assert cli1 is not cli2
        
        # But should load same config
        cli1.config["test"] = "value"
        # cli2's config should not be affected (different instances)
        assert "test" not in cli2.config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
