"""Tests for T_Λ Pulse"""
import pytest
from venom.sync.pulse import TLambdaPulse
import math


def test_pulse_initialization():
    """Test T_Λ pulse initialization"""
    pulse = TLambdaPulse(k=4, p=5, t1=0.001)
    assert pulse.k == 4
    assert pulse.p == 5
    assert pulse.t1 == 0.001


def test_pulse_stability_condition():
    """Test that kP > 1 condition is enforced"""
    # Valid: kP = 4*5 = 20 > 1
    pulse = TLambdaPulse(k=4, p=5)
    assert pulse.k * pulse.p > 1
    
    # Invalid: kP = 1*1 = 1, should raise ValueError
    with pytest.raises(ValueError, match="Stability condition violated"):
        TLambdaPulse(k=1, p=1)


def test_compute_t_lambda():
    """Test T_Λ computation"""
    pulse = TLambdaPulse(k=4, p=5, t1=0.001, u=54.598150033144236)
    t_lambda = pulse.compute_t_lambda()
    
    # T_Λ = (T1 * ln(U)) / (1 - 1/(kP))
    # T_Λ = (0.001 * ln(54.598)) / (1 - 1/20)
    # T_Λ = (0.001 * 4) / (0.95)
    # T_Λ ≈ 0.004211
    
    assert isinstance(t_lambda, float)
    assert t_lambda > 0
    assert t_lambda >= 1e-6  # Minimum bound
    assert abs(t_lambda - 0.004211) < 0.0001  # Approximate expected value


def test_generate_pulse():
    """Test pulse generation"""
    pulse = TLambdaPulse(k=4, p=5)
    
    pulse_data = pulse.generate_pulse()
    
    assert "pulse_id" in pulse_data
    assert "timestamp" in pulse_data
    assert "t_lambda" in pulse_data
    assert "k" in pulse_data
    assert "p" in pulse_data
    assert "kp" in pulse_data
    
    assert pulse_data["pulse_id"] == 1
    assert pulse_data["k"] == 4
    assert pulse_data["p"] == 5
    assert pulse_data["kp"] == 20


def test_pulse_sequence():
    """Test multiple pulse generation"""
    pulse = TLambdaPulse(k=4, p=5)
    
    pulse1 = pulse.generate_pulse()
    pulse2 = pulse.generate_pulse()
    pulse3 = pulse.generate_pulse()
    
    assert pulse1["pulse_id"] == 1
    assert pulse2["pulse_id"] == 2
    assert pulse3["pulse_id"] == 3


def test_pulse_reset():
    """Test pulse reset"""
    pulse = TLambdaPulse(k=4, p=5)
    
    pulse.generate_pulse()
    pulse.generate_pulse()
    assert pulse.pulse_count == 2
    
    pulse.reset()
    assert pulse.pulse_count == 0
    
    pulse_data = pulse.generate_pulse()
    assert pulse_data["pulse_id"] == 1


def test_next_pulse_delay():
    """Test next pulse delay calculation"""
    pulse = TLambdaPulse(k=4, p=5)
    delay = pulse.get_next_pulse_delay()
    
    assert isinstance(delay, float)
    assert delay > 0
    assert delay == pulse.compute_t_lambda()
