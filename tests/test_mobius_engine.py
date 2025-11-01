"""Tests for AdaptiveMobiusEngine"""

import pytest
from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine, CompressionResult


class TestAdaptiveMobiusEngine:
    """Test suite for AdaptiveMobiusEngine"""
    
    def test_engine_initialization_with_defaults(self):
        """Test engine initializes with defaults"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        assert engine is not None
        assert engine.config is not None
    
    def test_engine_initialization_with_manual_config(self):
        """Test engine with manual configuration"""
        config = {
            'n_cores': 8,
            'lambda_wrap': 400.0,
            'parallel_fraction': 0.80,
            'cpu_health': 0.7,
            'memory_health': 0.8,
            'thermal_health': 0.9
        }
        engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
        
        assert engine.config['n_cores'] == 8
        assert engine.config['lambda_wrap'] == 400.0
    
    def test_calculate_theta(self):
        """Test theta calculation"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = engine.calculate_theta(
            cpu_health=0.8,
            memory_health=0.7,
            thermal_health=0.9
        )
        
        # θ = 0.3*0.8 + 0.3*0.7 + 0.4*0.9 = 0.24 + 0.21 + 0.36 = 0.81
        expected = 0.3 * 0.8 + 0.3 * 0.7 + 0.4 * 0.9
        assert abs(theta - expected) < 0.001
    
    def test_theta_in_range(self):
        """Test theta is always in [0, 1]"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        
        # Test various inputs
        test_cases = [
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            (0.5, 0.5, 0.5),
            (0.2, 0.8, 0.6)
        ]
        
        for cpu, mem, therm in test_cases:
            theta = engine.calculate_theta(cpu, mem, therm)
            assert 0.0 <= theta <= 1.0
    
    def test_theta_compression_unwrap(self):
        """Test theta compression in UNWRAP mode (θ < 0.3)"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.2
        compression = engine.theta_compression(theta)
        
        # Should be 0.5 in UNWRAP mode
        assert compression == 0.5
    
    def test_theta_compression_balance(self):
        """Test theta compression in BALANCE mode (0.5 ≤ θ < 0.7)"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.6
        compression = engine.theta_compression(theta)
        
        # Θ = 1.0 + (0.6-0.5)×5.0 = 1.0 + 0.5 = 1.5
        expected = 1.0 + (theta - 0.5) * 5.0
        assert abs(compression - expected) < 0.001
    
    def test_theta_compression_wrap(self):
        """Test theta compression in WRAP mode (0.7 ≤ θ < 0.9)"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.8
        compression = engine.theta_compression(theta)
        
        # Θ = 2.0 + (0.8-0.7)×2.5 = 2.0 + 0.25 = 2.25
        expected = 2.0 + (theta - 0.7) * 2.5
        assert abs(compression - expected) < 0.001
    
    def test_theta_compression_optimize(self):
        """Test theta compression in OPTIMIZE mode (θ ≥ 0.9)"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.95
        compression = engine.theta_compression(theta)
        
        # Should be 3.0 in OPTIMIZE mode
        assert compression == 3.0
    
    def test_theta_compression_conservative_mode(self):
        """Test conservative compression mode"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.8
        
        normal = engine.theta_compression(theta, mode='adaptive')
        conservative = engine.theta_compression(theta, mode='conservative')
        
        # Conservative should be 75% of normal
        assert abs(conservative - normal * 0.75) < 0.001
    
    def test_theta_compression_aggressive_mode(self):
        """Test aggressive compression mode"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        theta = 0.8
        
        normal = engine.theta_compression(theta, mode='adaptive')
        aggressive = engine.theta_compression(theta, mode='aggressive')
        
        # Aggressive should be 125% of normal
        assert abs(aggressive - normal * 1.25) < 0.001
    
    def test_amdahl_speedup(self):
        """Test Amdahl's Law speedup calculation"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        
        # S_A = 1 / [(1-P) + P/N]
        # With P=0.75, N=4: S_A = 1 / [0.25 + 0.1875] = 1 / 0.4375 = 2.286
        s_a = engine.amdahl_speedup(n_cores=4, parallel_fraction=0.75)
        expected = 1.0 / ((1.0 - 0.75) + (0.75 / 4))
        
        assert abs(s_a - expected) < 0.001
    
    def test_amdahl_speedup_perfect_parallel(self):
        """Test Amdahl speedup with perfect parallelization"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        
        # P=1.0 (perfect parallel) should give S_A = N
        s_a = engine.amdahl_speedup(n_cores=8, parallel_fraction=1.0)
        assert abs(s_a - 8.0) < 0.001
    
    def test_amdahl_speedup_no_parallel(self):
        """Test Amdahl speedup with no parallelization"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        
        # P=0.0 (no parallel) should give S_A = 1
        s_a = engine.amdahl_speedup(n_cores=8, parallel_fraction=0.0)
        assert abs(s_a - 1.0) < 0.001
    
    def test_total_speedup(self):
        """Test total speedup calculation"""
        config = {
            'n_cores': 4,
            'lambda_wrap': 200.0,
            'parallel_fraction': 0.75,
            'cpu_health': 0.8,
            'memory_health': 0.8,
            'thermal_health': 0.8
        }
        engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
        
        # Calculate expected
        theta = 0.3 * 0.8 + 0.3 * 0.8 + 0.4 * 0.8  # = 0.8
        theta_comp = 2.0 + (0.8 - 0.7) * 2.5  # = 2.25 (WRAP mode)
        s_a = 1.0 / ((1.0 - 0.75) + (0.75 / 4))  # ~2.286
        expected = theta_comp * 200.0 * s_a  # ~1028.7
        
        s_total = engine.total_speedup()
        
        assert abs(s_total - expected) < 1.0  # Allow small margin
    
    def test_compress_time_returns_result(self):
        """Test compress_time returns CompressionResult"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        result = engine.compress_time(sequential_time=100.0)
        
        assert isinstance(result, CompressionResult)
    
    def test_compress_time_reduces_time(self):
        """Test time compression actually reduces time"""
        config = {
            'n_cores': 8,
            'lambda_wrap': 400.0,
            'parallel_fraction': 0.80,
            'cpu_health': 0.8,
            'memory_health': 0.8,
            'thermal_health': 0.8
        }
        engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
        
        sequential_time = 840.0  # 840 hours
        result = engine.compress_time(sequential_time)
        
        # Parallel time should be much less than sequential
        assert result.parallel_time < sequential_time
        assert result.speedup > 1.0
    
    def test_compress_time_fields(self):
        """Test CompressionResult has all required fields"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        result = engine.compress_time(sequential_time=100.0)
        
        assert hasattr(result, 'sequential_time')
        assert hasattr(result, 'parallel_time')
        assert hasattr(result, 'speedup')
        assert hasattr(result, 'theta')
        assert hasattr(result, 'theta_compression')
        assert hasattr(result, 'n_cores')
        assert hasattr(result, 'lambda_wrap')
        assert hasattr(result, 'parallel_fraction')
        assert hasattr(result, 'reduction_percent')
    
    def test_compress_time_reduction_percent(self):
        """Test reduction percentage calculation"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        result = engine.compress_time(sequential_time=100.0)
        
        # Reduction should match calculation
        expected_reduction = ((result.sequential_time - result.parallel_time) / 
                             result.sequential_time) * 100
        
        assert abs(result.reduction_percent - expected_reduction) < 0.1
    
    def test_get_mode_name(self):
        """Test mode name retrieval"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        
        assert engine.get_mode_name(0.2) == "UNWRAP"
        assert engine.get_mode_name(0.4) == "TRANSITION"
        assert engine.get_mode_name(0.6) == "BALANCE"
        assert engine.get_mode_name(0.8) == "WRAP"
        assert engine.get_mode_name(0.95) == "OPTIMIZE"
    
    def test_different_hardware_profiles(self):
        """Test compression with different hardware profiles"""
        # Raspberry Pi profile
        rpi_config = {
            'n_cores': 4,
            'lambda_wrap': 50.0,
            'parallel_fraction': 0.65,
            'cpu_health': 0.5,
            'memory_health': 0.6,
            'thermal_health': 0.7
        }
        
        # Cloud server profile
        cloud_config = {
            'n_cores': 32,
            'lambda_wrap': 832.0,
            'parallel_fraction': 0.95,
            'cpu_health': 0.9,
            'memory_health': 0.95,
            'thermal_health': 0.9
        }
        
        rpi_engine = AdaptiveMobiusEngine(auto_detect=False, override_config=rpi_config)
        cloud_engine = AdaptiveMobiusEngine(auto_detect=False, override_config=cloud_config)
        
        sequential = 840.0
        rpi_result = rpi_engine.compress_time(sequential)
        cloud_result = cloud_engine.compress_time(sequential)
        
        # Cloud should have much better speedup
        assert cloud_result.speedup > rpi_result.speedup
        assert cloud_result.parallel_time < rpi_result.parallel_time
    
    def test_print_compression_summary_no_error(self):
        """Test print_compression_summary doesn't raise errors"""
        engine = AdaptiveMobiusEngine(auto_detect=False)
        result = engine.compress_time(sequential_time=100.0)
        
        # Should not raise any exceptions
        engine.print_compression_summary(result)
