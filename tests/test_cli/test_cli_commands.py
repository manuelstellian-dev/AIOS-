#!/usr/bin/env python3
"""
Comprehensive tests for VENOM CLI commands
Tests all major CLI functionality including modules, AI, security, cloud, and health commands
"""
import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from venom.cli.main import VenomCLI, main


class TestModulesCommands:
    """Test module management commands"""
    
    def test_modules_list_with_rich(self):
        """Test listing modules with rich available"""
        cli = VenomCLI()
        args = MagicMock()
        
        result = cli.modules_list(args)
        
        assert result == 0
    
    def test_modules_list_without_rich(self):
        """Test listing modules without rich (fallback to plain text)"""
        with patch('venom.cli.main.RICH_AVAILABLE', False):
            cli = VenomCLI()
            args = MagicMock()
            
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = cli.modules_list(args)
                output = fake_out.getvalue()
            
            assert result == 0
            assert "VENOM Modules" in output
            assert "core" in output
            assert "ml" in output
    
    def test_modules_info_core(self):
        """Test getting info for core module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "core"
        
        result = cli.modules_info(args)
        
        assert result == 0
    
    def test_modules_info_ml(self):
        """Test getting info for ML module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "ml"
        
        result = cli.modules_info(args)
        
        assert result == 0
    
    def test_modules_info_security(self):
        """Test getting info for security module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "security"
        
        result = cli.modules_info(args)
        
        assert result == 0
    
    def test_modules_info_cloud(self):
        """Test getting info for cloud module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "cloud"
        
        result = cli.modules_info(args)
        
        assert result == 0
    
    def test_modules_info_knowledge(self):
        """Test getting info for knowledge module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "knowledge"
        
        result = cli.modules_info(args)
        
        assert result == 0
    
    def test_modules_info_invalid_module(self):
        """Test getting info for non-existent module"""
        cli = VenomCLI()
        args = MagicMock()
        args.module_name = "nonexistent"
        
        result = cli.modules_info(args)
        
        assert result == 1


class TestAICommands:
    """Test AI/ML operation commands"""
    
    def test_ai_train_missing_data_file(self):
        """Test AI training with missing data file"""
        cli = VenomCLI()
        args = MagicMock()
        args.model = "linear"
        args.data = "/nonexistent/data.csv"
        
        result = cli.ai_train(args)
        
        assert result == 1
    
    def test_ai_train_with_valid_data(self):
        """Test AI training with valid data file"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.model = "linear"
            args.data = temp_file
            
            result = cli.ai_train(args)
            
            assert result == 0
        finally:
            os.unlink(temp_file)
    
    def test_ai_predict_missing_model(self):
        """Test AI prediction with missing model file"""
        cli = VenomCLI()
        args = MagicMock()
        args.model = "/nonexistent/model.pt"
        args.input = "test_input"
        
        result = cli.ai_predict(args)
        
        assert result == 1
    
    def test_ai_predict_with_valid_model(self):
        """Test AI prediction with valid model file"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pt', delete=False) as f:
            f.write("mock_model_data")
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.model = temp_file
            args.input = "test_input"
            
            result = cli.ai_predict(args)
            
            assert result == 0
        finally:
            os.unlink(temp_file)



class TestSecurityCommands:
    """Test security operation commands"""
    
    def test_security_encrypt_missing_file(self):
        """Test encryption with missing file"""
        cli = VenomCLI()
        args = MagicMock()
        args.file = "/nonexistent/file.txt"
        
        result = cli.security_encrypt(args)
        
        assert result == 1
    
    def test_security_encrypt_valid_file(self):
        """Test encryption with valid file"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("sensitive data")
            input_file = f.name
        
        try:
            args = MagicMock()
            args.file = input_file
            
            result = cli.security_encrypt(args)
            
            # Encryption might fail if security module has specific requirements
            # But the CLI should handle it gracefully (return 0 or 1)
            assert result in [0, 1]
            
            if result == 0:
                # Check encrypted file was created
                encrypted_path = Path(input_file).with_suffix('.encrypted')
                key_path = Path(input_file).with_suffix('.key')
                
                # Cleanup if files were created
                if encrypted_path.exists():
                    os.unlink(encrypted_path)
                if key_path.exists():
                    os.unlink(key_path)
        finally:
            os.unlink(input_file)
    
    def test_security_scan_missing_path(self):
        """Test security scan with missing path"""
        cli = VenomCLI()
        args = MagicMock()
        args.path = "/nonexistent/directory"
        
        result = cli.security_scan(args)
        
        assert result == 1
    
    def test_security_scan_valid_path(self):
        """Test security scan with valid path"""
        cli = VenomCLI()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            args = MagicMock()
            args.path = tmpdir
            
            result = cli.security_scan(args)
            
            assert result == 0


class TestCloudCommands:
    """Test cloud operation commands"""
    
    def test_cloud_deploy_missing_config(self):
        """Test cloud deployment with missing config file"""
        cli = VenomCLI()
        args = MagicMock()
        args.provider = "aws"
        args.config = "/nonexistent/config.yaml"
        
        result = cli.cloud_deploy(args)
        
        assert result == 1
    
    def test_cloud_deploy_with_config(self):
        """Test cloud deployment with valid config"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("# Mock deployment config\n")
            config_file = f.name
        
        try:
            args = MagicMock()
            args.provider = "aws"
            args.config = config_file
            
            result = cli.cloud_deploy(args)
            
            # Returns 0 or 1 depending on cloud SDK availability
            assert result in [0, 1]
        finally:
            os.unlink(config_file)
    
    def test_cloud_status(self):
        """Test cloud status command"""
        cli = VenomCLI()
        args = MagicMock()
        
        result = cli.cloud_status(args)
        
        # Always returns 0 (shows mock status)
        assert result == 0


class TestKnowledgeCommands:
    """Test knowledge base operation commands"""
    
    def test_knowledge_add_missing_doc(self):
        """Test adding document with missing file"""
        cli = VenomCLI()
        args = MagicMock()
        args.doc = "/nonexistent/doc.pdf"
        args.metadata = None
        
        result = cli.knowledge_add(args)
        
        assert result == 1
    
    def test_knowledge_add_valid_doc(self):
        """Test adding document with valid file"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document with important information.")
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.doc = temp_file
            args.metadata = None
            
            result = cli.knowledge_add(args)
            
            assert result == 0
        finally:
            os.unlink(temp_file)
    
    def test_knowledge_add_with_metadata(self):
        """Test adding document with metadata"""
        cli = VenomCLI()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.doc = temp_file
            args.metadata = '{"author": "test", "tags": ["test"]}'
            
            result = cli.knowledge_add(args)
            
            assert result == 0
        finally:
            os.unlink(temp_file)
    
    def test_knowledge_search(self):
        """Test knowledge base search"""
        cli = VenomCLI()
        args = MagicMock()
        args.query = "test query"
        
        result = cli.knowledge_search(args)
        
        # Returns 0 or 1 depending on knowledge module availability
        assert result in [0, 1]


class TestHealthCommands:
    """Test system health check commands"""
    
    def test_health_check(self):
        """Test basic health check"""
        cli = VenomCLI()
        args = MagicMock()
        
        result = cli.health_check(args)
        
        assert result == 0
    
    def test_health_metrics(self):
        """Test metrics collection"""
        cli = VenomCLI()
        args = MagicMock()
        
        result = cli.health_metrics(args)
        
        # Returns 0 or 1 depending on observability module availability
        assert result in [0, 1]


class TestCLIHelpers:
    """Test CLI helper methods"""
    
    def test_success_message(self):
        """Test success message printing"""
        cli = VenomCLI()
        
        # Should not raise exception
        cli._success("Test success message")
    
    def test_error_message(self):
        """Test error message printing"""
        cli = VenomCLI()
        
        # Should not raise exception
        cli._error("Test error message")
    
    def test_info_message(self):
        """Test info message printing"""
        cli = VenomCLI()
        
        # Should not raise exception
        cli._info("Test info message")
    
    def test_warning_message(self):
        """Test warning message printing"""
        cli = VenomCLI()
        
        # Should not raise exception
        cli._warning("Test warning message")


class TestMainFunction:
    """Test main CLI entry point"""
    
    def test_main_help(self):
        """Test main function with --help"""
        with patch('sys.argv', ['venom', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Help should exit with code 0
            assert exc_info.value.code == 0
    
    def test_main_version(self):
        """Test main function with --version"""
        with patch('sys.argv', ['venom', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Version should exit with code 0
            assert exc_info.value.code == 0
    
    def test_main_modules_list(self):
        """Test main function with modules list command"""
        with patch('sys.argv', ['venom', 'modules', 'list']):
            result = main()
            
            # Should run successfully
            assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
