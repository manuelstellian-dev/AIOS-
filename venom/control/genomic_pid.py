"""
Genomic PID Controller
Maintains system stability (ΔV < 0) by recalibrating O flow weight
Prevents drift in the fractal organism
"""
import time
from typing import Dict, Any, Optional


class GenomicPID:
    """
    PID controller for genomic stability
    Ensures ΔV < 0 by adjusting optimization weight in O flow
    """
    
    def __init__(self, kp: float = 0.5, ki: float = 0.1, kd: float = 0.2, 
                 setpoint: float = 0.0):
        """
        Initialize Genomic PID controller
        
        Args:
            kp: Proportional gain
            ki: Integral gain  
            kd: Derivative gain
            setpoint: Target stability value (default 0 for ΔV < 0)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time: Optional[float] = None
        
        self.stability_history = []
        
    def compute(self, current_value: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Compute PID control output
        
        Args:
            current_value: Current system value (e.g., entropy level)
            timestamp: Optional timestamp, defaults to current time
            
        Returns:
            Control output and stability metrics
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Calculate error
        error = self.setpoint - current_value
        
        # Time delta
        if self.previous_time is None:
            dt = 0.0
        else:
            dt = timestamp - self.previous_time
            
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        if dt > 0:
            self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0:
            derivative = (error - self.previous_error) / dt
        else:
            derivative = 0.0
        d_term = self.kd * derivative
        
        # Total control output
        output = p_term + i_term + d_term
        
        # Calculate ΔV (stability delta)
        delta_v = error - self.previous_error
        stable = delta_v < 0
        
        # Update state
        self.previous_error = error
        self.previous_time = timestamp
        self.stability_history.append({
            "timestamp": timestamp,
            "delta_v": delta_v,
            "stable": stable
        })
        
        # Keep only recent history
        if len(self.stability_history) > 1000:
            self.stability_history = self.stability_history[-1000:]
        
        return {
            "pid_output": output,
            "p_term": p_term,
            "i_term": i_term,
            "d_term": d_term,
            "error": error,
            "delta_v": delta_v,
            "stable": stable,
            "adjustment": -output  # Negative feedback for recalibration
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
