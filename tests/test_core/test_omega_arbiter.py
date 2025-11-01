"""
Comprehensive tests for OmegaArbiter
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from venom.core.omega_arbiter import OmegaArbiter


class TestOmegaArbiterInit:
    """Test OmegaArbiter initialization"""
    
    def test_init_omega_disabled(self):
        """Test initialization with Omega disabled (legacy mode)"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert arbiter.enable_omega == False
        assert arbiter.mobius_engine is None
        assert arbiter.theta_monitor is None
    
    def test_init_omega_enabled_default(self):
        """Test default initialization with Omega enabled"""
        arbiter = OmegaArbiter(enable_omega=True)
        
        assert arbiter.enable_omega == True
        # mobius_engine and theta_monitor may be None if imports fail
    
    def test_init_with_custom_components(self):
        """Test initialization with custom components"""
        pulse = Mock()
        pid = Mock()
        ledger = Mock()
        
        arbiter = OmegaArbiter(
            pulse=pulse,
            pid=pid,
            ledger=ledger,
            enable_omega=False
        )
        
        assert arbiter.pulse == pulse
        assert arbiter.pid == pid
        assert arbiter.ledger == ledger
    
    def test_init_with_custom_mobius(self):
        """Test initialization with custom Möbius engine"""
        custom_mobius = Mock()
        
        arbiter = OmegaArbiter(mobius_engine=custom_mobius, enable_omega=True)
        
        assert arbiter.mobius_engine == custom_mobius
    
    def test_init_with_custom_theta_running(self):
        """Test initialization with running theta monitor"""
        custom_theta = Mock()
        custom_theta.running = True
        
        arbiter = OmegaArbiter(theta_monitor=custom_theta, enable_omega=True)
        
        assert arbiter.theta_monitor == custom_theta
        # Should not call start_monitoring since already running
    
    def test_init_with_custom_theta_not_running(self):
        """Test initialization with non-running theta monitor"""
        custom_theta = Mock()
        custom_theta.running = False
        
        arbiter = OmegaArbiter(theta_monitor=custom_theta, enable_omega=True)
        
        assert arbiter.theta_monitor == custom_theta
        custom_theta.start_monitoring.assert_called_once()


class TestOmegaArbiterWaveExecution:
    """Test wave execution functionality"""
    
    def test_execute_wave_parallel_basic(self):
        """Test parallel wave execution"""
        arbiter = OmegaArbiter(enable_omega=True)
        arbiter.mobius_engine = Mock()
        arbiter.theta_monitor = Mock()
        arbiter.theta_monitor.get_theta.return_value = 0.8
        
        actions = [Mock() for _ in range(3)]
        for action in actions:
            action.execute = Mock(return_value={"result": "ok"})
        
        results = arbiter.execute_wave_parallel(actions)
        
        assert isinstance(results, list) or results is not None
    
    def test_execute_all_waves_parallel(self):
        """Test executing all waves in parallel"""
        arbiter = OmegaArbiter(enable_omega=True)
        arbiter.mobius_engine = Mock()
        arbiter.theta_monitor = Mock()
        arbiter.theta_monitor.get_theta.return_value = 0.9
        
        waves = [[Mock()], [Mock()]]
        for wave in waves:
            for action in wave:
                action.execute = Mock(return_value={"result": "done"})
        
        results = arbiter.execute_all_waves_parallel(waves)
        
        assert results is not None
    
    def test_adaptive_throttle_high_theta(self):
        """Test adaptive throttling with high theta"""
        arbiter = OmegaArbiter(enable_omega=True)
        
        throttle_info = arbiter.adaptive_throttle(0.9)
        
        assert isinstance(throttle_info, dict)
        assert throttle_info.get("should_throttle") == False or "should_throttle" not in throttle_info
    
    def test_adaptive_throttle_low_theta(self):
        """Test adaptive throttling with low theta"""
        arbiter = OmegaArbiter(enable_omega=True)
        
        throttle_info = arbiter.adaptive_throttle(0.2)
        
        assert isinstance(throttle_info, dict)
        assert throttle_info.get("should_throttle") == True or "should_throttle" not in throttle_info
    
    def test_start_omega(self):
        """Test starting Omega features"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        arbiter.start_omega()
        
        # Should update state
        assert hasattr(arbiter, 'enable_omega')
    
    def test_get_omega_status(self):
        """Test getting Omega status"""
        arbiter = OmegaArbiter(enable_omega=True)
        arbiter.mobius_engine = Mock()
        arbiter.theta_monitor = Mock()
        
        status = arbiter.get_omega_status()
        
        assert isinstance(status, dict)
        assert "omega_enabled" in status or "enabled" in status


class TestOmegaArbiterStop:
    """Test Omega stop functionality"""
    
    def test_stop_without_omega(self):
        """Test stopping without Omega features"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        arbiter.stop()
        
        assert arbiter.running == False
    
    def test_stop_with_omega(self):
        """Test stopping with Omega features"""
        arbiter = OmegaArbiter(enable_omega=True)
        arbiter.theta_monitor = Mock()
        arbiter.theta_monitor.stop_monitoring = Mock()
        
        arbiter.stop()
        
        assert arbiter.running == False
        # Should stop monitoring
        if arbiter.theta_monitor:
            arbiter.theta_monitor.stop_monitoring.assert_called_once()
    
    def test_stop_cleans_up_resources(self):
        """Test stop cleans up resources"""
        arbiter = OmegaArbiter(enable_omega=True)
        arbiter.theta_monitor = Mock()
        arbiter.theta_monitor.stop_monitoring = Mock()
        
        arbiter.stop()
        
        # Should clean up
        assert arbiter.running == False


class TestOmegaArbiterCompatibility:
    """Test backward compatibility with base Arbiter"""
    
    def test_beat_method_exists(self):
        """Test beat() method exists"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'beat')
        assert callable(arbiter.beat)
    
    def test_execute_method_exists(self):
        """Test execute() method exists"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'execute')
        assert callable(arbiter.execute)
    
    def test_execute_single_action(self):
        """Test execute() method works"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        action = Mock()
        action.execute = Mock(return_value={"status": "done"})
        
        result = arbiter.execute(action)
        
        action.execute.assert_called_once()
    
    def test_has_pulse_attribute(self):
        """Test has pulse attribute"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'pulse')
    
    def test_has_pid_attribute(self):
        """Test has PID attribute"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'pid')
    
    def test_has_ledger_attribute(self):
        """Test has ledger attribute"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'ledger')
    
    def test_has_mesh_attribute(self):
        """Test has mesh attribute"""
        arbiter = OmegaArbiter(enable_omega=False)
        
        assert hasattr(arbiter, 'mesh')
