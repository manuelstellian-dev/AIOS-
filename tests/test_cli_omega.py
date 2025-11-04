"""
Comprehensive tests for venom/cli/omega_cli.py
Tests all CLI commands with mocked dependencies
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from venom.cli import omega_cli


class TestCmdScan:
    """Tests for cmd_scan command"""
    
    @patch('venom.cli.omega_cli.UniversalHardwareScanner')
    @patch('builtins.print')
    def test_cmd_scan_success(self, mock_print, mock_scanner_class):
        """Test successful hardware scan"""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = {'cpu': 4}
        mock_scanner.print_profile.return_value = None
        mock_scanner_class.return_value = mock_scanner
        
        result = omega_cli.cmd_scan()
        
        assert result == 0
        mock_scanner_class.assert_called_once()
        mock_scanner.scan.assert_called_once()
        mock_scanner.print_profile.assert_called_once()
    
    @patch('venom.cli.omega_cli.UniversalHardwareScanner', side_effect=ImportError("Module not found"))
    @patch('builtins.print')
    def test_cmd_scan_import_error(self, mock_print, mock_scanner):
        """Test scan with missing dependencies"""
        result = omega_cli.cmd_scan()
        
        assert result == 1
        # Should print error message
        assert any('Error' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.UniversalHardwareScanner')
    @patch('builtins.print')
    def test_cmd_scan_general_error(self, mock_print, mock_scanner_class):
        """Test scan with general exception"""
        mock_scanner_class.side_effect = RuntimeError("Scan failed")
        
        result = omega_cli.cmd_scan()
        
        assert result == 1
        assert any('Scan failed' in str(call) for call in mock_print.call_args_list)


class TestCmdCompress:
    """Tests for cmd_compress command"""
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine')
    @patch('builtins.print')
    def test_cmd_compress_success(self, mock_print, mock_engine_class):
        """Test successful compression calculation"""
        mock_engine = Mock()
        mock_result = {'compressed_time': 100}
        mock_engine.compress_time.return_value = mock_result
        mock_engine.print_compression_summary.return_value = None
        mock_engine_class.return_value = mock_engine
        
        result = omega_cli.cmd_compress(840.0)
        
        assert result == 0
        mock_engine_class.assert_called_once_with(auto_detect=True)
        mock_engine.compress_time.assert_called_once_with(840.0)
        mock_engine.print_compression_summary.assert_called_once_with(mock_result)
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine', side_effect=ImportError("Module not found"))
    @patch('builtins.print')
    def test_cmd_compress_import_error(self, mock_print, mock_engine):
        """Test compress with missing dependencies"""
        result = omega_cli.cmd_compress(100.0)
        
        assert result == 1
        assert any('Error' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine')
    @patch('builtins.print')
    def test_cmd_compress_general_error(self, mock_print, mock_engine_class):
        """Test compress with general exception"""
        mock_engine_class.side_effect = RuntimeError("Compression failed")
        
        result = omega_cli.cmd_compress(100.0)
        
        assert result == 1
        assert any('failed' in str(call) for call in mock_print.call_args_list)


class TestCmdBenchmark:
    """Tests for cmd_benchmark command"""
    
    @patch('venom.cli.omega_cli.ParallelWaveExecutor')
    @patch('builtins.print')
    def test_cmd_benchmark_success(self, mock_print, mock_executor_class):
        """Test successful benchmark"""
        mock_executor = Mock()
        mock_result = Mock()
        mock_result.total_tasks = 25
        mock_result.completed_tasks = 25
        mock_result.failed_tasks = 0
        mock_result.total_time = 10.0
        mock_result.speedup = 5.0
        mock_executor.execute_parallel.return_value = mock_result
        mock_executor_class.return_value = mock_executor
        
        result = omega_cli.cmd_benchmark()
        
        assert result == 0
        mock_executor.execute_parallel.assert_called_once()
        # Check that waves were created
        waves = mock_executor.execute_parallel.call_args[0][0]
        assert len(waves) == 5  # 5 waves
    
    @patch('venom.cli.omega_cli.ParallelWaveExecutor', side_effect=ImportError("Module not found"))
    @patch('builtins.print')
    def test_cmd_benchmark_import_error(self, mock_print, mock_executor):
        """Test benchmark with missing dependencies"""
        result = omega_cli.cmd_benchmark()
        
        assert result == 1
        assert any('Error' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.ParallelWaveExecutor')
    @patch('builtins.print')
    def test_cmd_benchmark_general_error(self, mock_print, mock_executor_class):
        """Test benchmark with general exception"""
        mock_executor_class.side_effect = RuntimeError("Benchmark failed")
        
        result = omega_cli.cmd_benchmark()
        
        assert result == 1
        assert any('failed' in str(call) for call in mock_print.call_args_list)


class TestCmdMonitor:
    """Tests for cmd_monitor command"""
    
    @patch('venom.cli.omega_cli.time.sleep')
    @patch('venom.cli.omega_cli.ThetaMonitor')
    @patch('builtins.print')
    def test_cmd_monitor_success(self, mock_print, mock_monitor_class, mock_sleep):
        """Test successful monitoring"""
        mock_monitor = Mock()
        mock_monitor.start_monitoring.return_value = None
        mock_monitor.stop_monitoring.return_value = None
        mock_monitor.print_status.return_value = None
        mock_monitor_class.return_value = mock_monitor
        
        result = omega_cli.cmd_monitor(duration=4)
        
        assert result == 0
        mock_monitor_class.assert_called_once_with(interval=1.0)
        mock_monitor.start_monitoring.assert_called_once()
        mock_monitor.stop_monitoring.assert_called_once()
        assert mock_monitor.print_status.call_count == 2  # duration=4, every 2nd iteration
    
    @patch('venom.cli.omega_cli.time.sleep', side_effect=KeyboardInterrupt())
    @patch('venom.cli.omega_cli.ThetaMonitor')
    @patch('builtins.print')
    def test_cmd_monitor_keyboard_interrupt(self, mock_print, mock_monitor_class, mock_sleep):
        """Test monitoring with keyboard interrupt"""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        result = omega_cli.cmd_monitor(duration=10)
        
        assert result == 0
        mock_monitor.stop_monitoring.assert_called_once()
        assert any('Interrupted' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.ThetaMonitor', side_effect=ImportError("Module not found"))
    @patch('builtins.print')
    def test_cmd_monitor_import_error(self, mock_print, mock_monitor):
        """Test monitor with missing dependencies"""
        result = omega_cli.cmd_monitor(duration=10)
        
        assert result == 1
        assert any('Error' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.ThetaMonitor')
    @patch('builtins.print')
    def test_cmd_monitor_general_error(self, mock_print, mock_monitor_class):
        """Test monitor with general exception"""
        mock_monitor_class.side_effect = RuntimeError("Monitor failed")
        
        result = omega_cli.cmd_monitor(duration=10)
        
        assert result == 1
        assert any('failed' in str(call) for call in mock_print.call_args_list)


class TestCmdConfig:
    """Tests for cmd_config command"""
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine')
    @patch('venom.cli.omega_cli.UniversalHardwareScanner')
    @patch('builtins.print')
    def test_cmd_config_success(self, mock_print, mock_scanner_class, mock_engine_class):
        """Test successful config display"""
        # Mock scanner
        mock_scanner = Mock()
        mock_profile = Mock()
        mock_profile.platform_system = "Linux"
        mock_profile.platform_machine = "x86_64"
        mock_profile.cpu_cores_logical = 8
        mock_profile.cpu_vendor = "Intel"
        mock_profile.memory_total_gb = 16.0
        mock_profile.has_cuda = True
        mock_profile.has_rocm = False
        mock_profile.has_metal = False
        mock_scanner.scan.return_value = mock_profile
        mock_scanner_class.return_value = mock_scanner
        
        # Mock engine
        mock_engine = Mock()
        mock_engine.config = {
            'n_cores': 8,
            'lambda_wrap': 4.0,
            'parallel_fraction': 0.8
        }
        mock_engine.calculate_theta.return_value = 0.75
        mock_engine.get_mode_name.return_value = "High Performance"
        mock_engine.total_speedup.return_value = 5.5
        mock_engine_class.return_value = mock_engine
        
        result = omega_cli.cmd_config()
        
        assert result == 0
        mock_scanner_class.assert_called_once()
        mock_engine_class.assert_called_once_with(auto_detect=True)
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine')
    @patch('venom.cli.omega_cli.UniversalHardwareScanner')
    @patch('builtins.print')
    def test_cmd_config_no_gpu(self, mock_print, mock_scanner_class, mock_engine_class):
        """Test config display with no GPU"""
        # Mock scanner with no GPU
        mock_scanner = Mock()
        mock_profile = Mock()
        mock_profile.platform_system = "Linux"
        mock_profile.platform_machine = "x86_64"
        mock_profile.cpu_cores_logical = 4
        mock_profile.cpu_vendor = "AMD"
        mock_profile.memory_total_gb = 8.0
        mock_profile.has_cuda = False
        mock_profile.has_rocm = False
        mock_profile.has_metal = False
        mock_scanner.scan.return_value = mock_profile
        mock_scanner_class.return_value = mock_scanner
        
        # Mock engine
        mock_engine = Mock()
        mock_engine.config = {'n_cores': 4}
        mock_engine.calculate_theta.return_value = 0.5
        mock_engine.get_mode_name.return_value = "Standard"
        mock_engine.total_speedup.return_value = 2.0
        mock_engine_class.return_value = mock_engine
        
        result = omega_cli.cmd_config()
        
        assert result == 0
        # Should print "None" for GPU
        assert any('None' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine', side_effect=ImportError("Module not found"))
    @patch('builtins.print')
    def test_cmd_config_import_error(self, mock_print, mock_engine):
        """Test config with missing dependencies"""
        result = omega_cli.cmd_config()
        
        assert result == 1
        assert any('Error' in str(call) for call in mock_print.call_args_list)
    
    @patch('venom.cli.omega_cli.AdaptiveMobiusEngine')
    @patch('venom.cli.omega_cli.UniversalHardwareScanner')
    @patch('builtins.print')
    def test_cmd_config_general_error(self, mock_print, mock_scanner_class, mock_engine_class):
        """Test config with general exception"""
        mock_scanner_class.side_effect = RuntimeError("Config failed")
        
        result = omega_cli.cmd_config()
        
        assert result == 1
        assert any('failed' in str(call) for call in mock_print.call_args_list)


class TestMain:
    """Tests for main CLI function"""
    
    @patch('venom.cli.omega_cli.cmd_scan', return_value=0)
    @patch('sys.argv', ['omega_cli', 'scan'])
    def test_main_scan_command(self, mock_cmd):
        """Test main with scan command"""
        result = omega_cli.main()
        assert result == 0
        mock_cmd.assert_called_once()
    
    @patch('venom.cli.omega_cli.cmd_compress', return_value=0)
    @patch('sys.argv', ['omega_cli', 'compress', '100'])
    def test_main_compress_command(self, mock_cmd):
        """Test main with compress command"""
        result = omega_cli.main()
        assert result == 0
        mock_cmd.assert_called_once_with(100.0)
    
    @patch('venom.cli.omega_cli.cmd_benchmark', return_value=0)
    @patch('sys.argv', ['omega_cli', 'benchmark'])
    def test_main_benchmark_command(self, mock_cmd):
        """Test main with benchmark command"""
        result = omega_cli.main()
        assert result == 0
        mock_cmd.assert_called_once()
    
    @patch('venom.cli.omega_cli.cmd_monitor', return_value=0)
    @patch('sys.argv', ['omega_cli', 'monitor', '--duration', '30'])
    def test_main_monitor_command(self, mock_cmd):
        """Test main with monitor command"""
        result = omega_cli.main()
        assert result == 0
        mock_cmd.assert_called_once_with(30)
    
    @patch('venom.cli.omega_cli.cmd_config', return_value=0)
    @patch('sys.argv', ['omega_cli', 'config'])
    def test_main_config_command(self, mock_cmd):
        """Test main with config command"""
        result = omega_cli.main()
        assert result == 0
        mock_cmd.assert_called_once()
    
    @patch('sys.argv', ['omega_cli'])
    @patch('builtins.print')
    def test_main_no_command(self, mock_print):
        """Test main with no command (should show help)"""
        result = omega_cli.main()
        assert result == 1
    
    @patch('sys.argv', ['omega_cli', 'invalid'])
    @patch('builtins.print')
    def test_main_invalid_command(self, mock_print):
        """Test main with invalid command"""
        with pytest.raises(SystemExit):
            omega_cli.main()
