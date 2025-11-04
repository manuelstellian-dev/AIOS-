"""Tests for Genomic PID Controller"""
import pytest
from venom.control.genomic_pid import GenomicPID


def test_pid_initialization():
    """Test PID initialization"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    assert pid.kp == 0.6
    assert pid.ki == 0.1
    assert pid.kd == 0.05
    assert pid.t_threshold == 0.02
    assert pid.integral == 0.0
    assert pid.previous_error == 0.0


def test_pid_compute():
    """Test PID computation"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Test with t_lambda below threshold
    result = pid.compute(t_lambda=0.01)
    
    assert "pid_out" in result
    assert "p_term" in result
    assert "i_term" in result
    assert "d_term" in result
    assert "delta_t" in result
    assert "delta_v" in result
    assert "stable" in result
    assert "weight_adjustment" in result
    
    # ΔT = t_lambda - t_threshold = 0.01 - 0.02 = -0.01
    assert result["delta_t"] == pytest.approx(-0.01)
    assert result["stable"] == True  # ΔV < 0


def test_pid_anti_windup():
    """Test PID anti-windup clamping"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Force large integral by repeated calls with high error
    for _ in range(100):
        pid.compute(t_lambda=1.0, timestamp=0.1 * _)
    
    # Integral should be clamped to [-1.0, 1.0]
    assert pid.integral >= -1.0
    assert pid.integral <= 1.0


def test_pid_history_trimming():
    """Test PID history is trimmed to last 1000 entries"""
    pid = GenomicPID()
    
    # Add more than 1000 entries
    for i in range(1500):
        pid.compute(t_lambda=0.01 + i * 0.001, timestamp=float(i))
    
    # History should be trimmed to 1000
    assert len(pid.stability_history) == 1000
    # Should keep the most recent ones
    assert pid.stability_history[-1]["timestamp"] == 1499.0


def test_pid_epsilon_reset():
    """Test ε-reset when error is very small"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Build up some integral with sustained error
    for i in range(5):
        pid.compute(t_lambda=0.05, timestamp=float(i))
    
    # Should have non-zero integral now
    assert abs(pid.integral) > 0.01
    
    # Compute with very small error (|ΔT| < 1e-4)
    # t_lambda very close to t_threshold
    pid.compute(t_lambda=0.02000001, timestamp=10.0)
    
    # Integral should be reset to 0 (or very close due to floating point)
    assert abs(pid.integral) < 1e-6


def test_pid_weight_adjustment():
    """Test weight adjustment is limited to ±0.05"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Test with large error to potentially exceed limit
    result = pid.compute(t_lambda=10.0)
    
    # Weight adjustment should be clamped
    assert result["weight_adjustment"] >= -0.05
    assert result["weight_adjustment"] <= 0.05


def test_pid_stability_check():
    """Test is_stable method"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Not enough history
    assert pid.is_stable(window=10) == False
    
    # Build stable history (ΔV < 0)
    for i in range(15):
        pid.compute(t_lambda=0.02 - 0.001 * i, timestamp=float(i))
    
    # Should be stable over window of 10
    assert pid.is_stable(window=10) == True


def test_pid_update_params():
    """Test updating PID parameters"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05)
    
    pid.update_params(kp=0.7, ki=0.2, kd=0.1)
    
    assert pid.kp == 0.7
    assert pid.ki == 0.2
    assert pid.kd == 0.1


def test_pid_reset():
    """Test PID reset"""
    pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
    
    # Build some state
    pid.compute(t_lambda=0.05)
    pid.compute(t_lambda=0.06)
    
    assert pid.integral != 0.0
    assert pid.previous_error != 0.0
    assert len(pid.stability_history) > 0
    
    # Reset
    pid.reset()
    
    assert pid.integral == 0.0
    assert pid.previous_error == 0.0
    assert pid.previous_time is None
    assert len(pid.stability_history) == 0
