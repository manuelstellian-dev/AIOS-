"""
Genomic PID Controller
Maintains system stability (ΔV < 0) by recalibrating O flow weight
Prevents drift in the fractal organism

Implements:
- Error ΔT = T_Λ - T_threshold (where T_threshold = 0.02)
- Anti-windup: integral clamped to [-1.0, 1.0]
- ε-reset: integral reset to 0 when |ΔT| < 1e-4
- Weight adjustment: ΔO limited to ±0.05 per beat
"""
import time
from typing import Dict, Any, Optional


class GenomicPID:
    """
    PID controller for genomic stability
    Ensures ΔV < 0 by adjusting optimization weight in O flow
    
    Uses parameters from BalanceCore: Kp=0.6, Ki=0.1, Kd=0.05
    """
    
    def __init__(self, kp: float = 0.6, ki: float = 0.1, kd: float = 0.05, 
                 t_threshold: float = 0.02):
        """
        Initialize Genomic PID controller
        
        Args:
            kp: Proportional gain (default 0.6 from BalanceCore)
            ki: Integral gain (default 0.1 from BalanceCore)
            kd: Derivative gain (default 0.05 from BalanceCore)
            t_threshold: Time threshold for error calculation (default 0.02)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.t_threshold = t_threshold
        
        # State variables
        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time: Optional[float] = None
        
        # Constants
        self.INTEGRAL_CLAMP_MIN = -1.0
        self.INTEGRAL_CLAMP_MAX = 1.0
        self.EPSILON_RESET = 1e-4
        self.MAX_WEIGHT_DELTA = 0.05
        
        self.stability_history = []
    
    def update_params(self, kp: float, ki: float, kd: float):
        """Update PID parameters (typically from BalanceCore)"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
    def compute(self, t_lambda: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Compute PID control output for T_Λ
        
        Args:
            t_lambda: Current T_Λ value
            timestamp: Optional timestamp, defaults to current time
            
        Returns:
            Control output and stability metrics
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Calculate error: ΔT = T_Λ - T_threshold
        delta_t = t_lambda - self.t_threshold
        
        # Time delta
        if self.previous_time is None:
            dt = 0.0
        else:
            dt = timestamp - self.previous_time
            
        # ε-reset: Reset integral if error is very small
        if abs(delta_t) < self.EPSILON_RESET:
            self.integral = 0.0
            
        # Proportional term
        p_term = self.kp * delta_t
        
        # Integral term with anti-windup clamping
        if dt > 0:
            self.integral += delta_t * dt
            # Apply anti-windup clamping to [-1.0, 1.0]
            self.integral = max(self.INTEGRAL_CLAMP_MIN, 
                               min(self.INTEGRAL_CLAMP_MAX, self.integral))
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0 and self.previous_time is not None:
            derivative = (delta_t - self.previous_error) / dt
        else:
            derivative = 0.0
        d_term = self.kd * derivative
        
        # Total PID output
        pid_out = p_term + i_term + d_term
        
        # Calculate weight adjustment (limited to ±0.05)
        weight_adjustment = -pid_out  # Negative feedback
        weight_adjustment = max(-self.MAX_WEIGHT_DELTA, 
                               min(self.MAX_WEIGHT_DELTA, weight_adjustment))
        
        # Calculate ΔV (stability delta)
        delta_v = delta_t - self.previous_error
        stable = delta_v < 0
        
        # Update state
        self.previous_error = delta_t
        self.previous_time = timestamp
        self.stability_history.append({
            "timestamp": timestamp,
            "delta_t": delta_t,
            "delta_v": delta_v,
            "stable": stable
        })
        
        # Keep only recent history
        if len(self.stability_history) > 1000:
            self.stability_history = self.stability_history[-1000:]
        
        return {
            "pid_out": pid_out,
            "p_term": p_term,
            "i_term": i_term,
            "d_term": d_term,
            "delta_t": delta_t,
            "delta_v": delta_v,
            "stable": stable,
            "weight_adjustment": weight_adjustment,
            "integral": self.integral
        }
    
    def reset(self):
        """Reset PID controller state"""
        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time = None
        self.stability_history = []
        
    def is_stable(self, window: int = 10) -> bool:
        """
        Check if system has been stable over recent window
        
        Args:
            window: Number of recent samples to check
            
        Returns:
            True if all recent samples show ΔV < 0
        """
        if len(self.stability_history) < window:
            return False
            
        recent = self.stability_history[-window:]
        return all(sample["stable"] for sample in recent)
