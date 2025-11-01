"""
Tests for Graceful Shutdown Module
"""
import pytest
import signal
import sys
from unittest.mock import Mock, MagicMock, patch, call
from venom.ops.shutdown import GracefulShutdown


class TestGracefulShutdown:
    """Test GracefulShutdown functionality"""
    
    def test_initialization(self):
        """Test graceful shutdown initialization"""
        arbiter = Mock()
        
        with patch('signal.signal') as mock_signal:
            shutdown = GracefulShutdown(arbiter)
            
            # Verify signal handlers registered
            assert mock_signal.call_count == 2
            mock_signal.assert_any_call(signal.SIGTERM, shutdown._signal_handler)
            mock_signal.assert_any_call(signal.SIGINT, shutdown._signal_handler)
            
            assert shutdown.arbiter == arbiter
            assert shutdown.shutdown_requested == False
    
    def test_sigterm_handler(self):
        """Test SIGTERM signal handling"""
        arbiter = Mock()
        arbiter.running = True
        arbiter.beat_count = 100
        arbiter.mesh = None
        arbiter.ledger = Mock()
        arbiter.ledger.get_chain_length = Mock(return_value=50)
        arbiter.ledger.record_action = Mock()
        arbiter.ledger.get_manifest = Mock(return_value={'merkle_root': 'abcd1234' * 8})
        arbiter.executor = Mock()
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=True)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            # Mock sys.exit to prevent actual exit
            with patch('sys.exit') as mock_exit:
                shutdown._signal_handler(signal.SIGTERM, None)
                
                # Verify shutdown was executed
                assert shutdown.shutdown_requested == True
                assert arbiter.running == False
                arbiter.ledger.record_action.assert_called_once()
                arbiter.executor.shutdown.assert_called_once_with(wait=True, cancel_futures=False)
                mock_exit.assert_called_once_with(0)
    
    def test_sigint_handler(self):
        """Test SIGINT signal handling"""
        arbiter = Mock()
        arbiter.running = True
        arbiter.beat_count = 50
        arbiter.mesh = None
        arbiter.ledger = Mock()
        arbiter.ledger.get_chain_length = Mock(return_value=25)
        arbiter.ledger.record_action = Mock()
        arbiter.ledger.get_manifest = Mock(return_value={'merkle_root': 'xyz123' * 8})
        arbiter.executor = Mock()
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=False)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            with patch('sys.exit') as mock_exit:
                shutdown._signal_handler(signal.SIGINT, None)
                
                assert shutdown.shutdown_requested == True
                assert arbiter.running == False
                mock_exit.assert_called_once_with(0)
    
    def test_duplicate_shutdown_prevented(self):
        """Test that duplicate shutdown requests are ignored"""
        arbiter = Mock()
        arbiter.running = True
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            shutdown.shutdown_requested = True
            
            # Try to call shutdown again
            with patch.object(shutdown, 'shutdown') as mock_shutdown:
                shutdown._signal_handler(signal.SIGTERM, None)
                
                # Shutdown should not be called again
                mock_shutdown.assert_not_called()
    
    def test_shutdown_with_mesh(self):
        """Test shutdown with P2P mesh active"""
        arbiter = Mock()
        arbiter.running = True
        arbiter.beat_count = 200
        arbiter.mesh = Mock()
        arbiter.mesh.stop = Mock()
        arbiter.ledger = Mock()
        arbiter.ledger.get_chain_length = Mock(return_value=100)
        arbiter.ledger.record_action = Mock()
        arbiter.ledger.get_manifest = Mock(return_value={'merkle_root': 'test' * 16})
        arbiter.executor = Mock()
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=True)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            with patch('sys.exit'):
                shutdown.shutdown()
                
                # Verify mesh was stopped
                arbiter.mesh.stop.assert_called_once()
    
    def test_shutdown_ledger_error_handling(self):
        """Test shutdown handles ledger errors gracefully"""
        arbiter = Mock()
        arbiter.running = True
        arbiter.beat_count = 10
        arbiter.mesh = None
        arbiter.ledger = Mock()
        arbiter.ledger.record_action = Mock(side_effect=Exception("Ledger error"))
        arbiter.ledger.get_chain_length = Mock(return_value=5)
        arbiter.executor = Mock()
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=True)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            # Should not raise exception
            with patch('sys.exit'):
                shutdown.shutdown()
                
                # Executor should still be shut down
                arbiter.executor.shutdown.assert_called_once()
    
    def test_shutdown_general_error_handling(self):
        """Test shutdown handles general errors gracefully"""
        arbiter = Mock()
        arbiter.running = True
        # Make executor.shutdown raise an exception
        arbiter.executor = Mock()
        arbiter.executor.shutdown = Mock(side_effect=Exception("Executor error"))
        arbiter.beat_count = 5
        arbiter.mesh = None
        arbiter.ledger = Mock()
        arbiter.ledger.get_chain_length = Mock(return_value=3)
        arbiter.ledger.record_action = Mock()
        arbiter.ledger.get_manifest = Mock(return_value={'merkle_root': 'abc' * 16})
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=True)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            # Should handle error and exit
            with patch('sys.exit') as mock_exit:
                shutdown.shutdown()
                
                mock_exit.assert_called_once_with(0)
    
    def test_shutdown_sequence_order(self):
        """Test that shutdown happens in correct order"""
        arbiter = Mock()
        arbiter.running = True
        arbiter.beat_count = 42
        arbiter.mesh = Mock()
        arbiter.ledger = Mock()
        arbiter.ledger.get_chain_length = Mock(return_value=21)
        arbiter.ledger.get_manifest = Mock(return_value={'merkle_root': 'order' * 16})
        arbiter.executor = Mock()
        arbiter.pid = Mock()
        arbiter.pid.is_stable = Mock(return_value=True)
        
        call_order = []
        
        def track_arbiter_stop():
            call_order.append('arbiter')
        
        def track_mesh_stop():
            call_order.append('mesh')
        
        def track_ledger_record(*args, **kwargs):
            call_order.append('ledger')
        
        def track_executor_shutdown(**kwargs):
            call_order.append('executor')
        
        arbiter.running = property(lambda self: True, lambda self, value: call_order.append('arbiter') if not value else None)
        arbiter.mesh.stop = Mock(side_effect=track_mesh_stop)
        arbiter.ledger.record_action = Mock(side_effect=track_ledger_record)
        arbiter.executor.shutdown = Mock(side_effect=track_executor_shutdown)
        
        with patch('signal.signal'):
            shutdown = GracefulShutdown(arbiter)
            
            with patch('sys.exit'):
                shutdown.shutdown()
                
                # Verify order: mesh -> ledger -> executor
                assert 'mesh' in call_order
                assert 'ledger' in call_order
                assert 'executor' in call_order
                assert call_order.index('mesh') < call_order.index('ledger')
                assert call_order.index('ledger') < call_order.index('executor')
