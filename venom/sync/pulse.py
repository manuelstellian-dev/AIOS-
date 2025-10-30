"""
T_Λ Pulse - Time compression synchronization mechanism
Provides the temporal heartbeat for the fractal organism

Formula: T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP)) for kP > 1
"""
import time
import math
from typing import Dict, Any


class TLambdaPulse:
    """
    T_Λ Pulse generator implementing time compression equation
    Synchronizes all parallel flows with a fractal temporal rhythm
    
    Uses the formula: T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP))
    where:
    - T1 = 0.001 (base time)
    - k = 4 (number of parallel flows)
    - P = 5 (number of nodes, default)
    - U = exp(4) ≈ 54.6 (base, ln(U) ≈ 4)
    """
    
    def __init__(self, k: int = 4, p: int = 5, t1: float = 0.001, u: float = 54.598150033144236):
        """
        Initialize T_Λ pulse generator
        
        Args:
            k: Number of parallel flows (default 4)
            p: Number of nodes (default 5)
            t1: Base time in seconds (default 0.001)
            u: Base value, exp(4) (default ~54.6)
        """
        self.k = k
        self.p = p
        self.t1 = t1
        self.u = u
        self.start_time = time.time()
        self.pulse_count = 0
        
        # Verify stability condition: kP > 1
        if self.k * self.p <= 1:
            raise ValueError(f"Stability condition violated: kP = {self.k * self.p} must be > 1")
        
    def compute_t_lambda(self) -> float:
        """
        Compute T_Λ using the time compression formula
        
        Formula: T_Λ(k, P, U) = (T1 * ln(U)) / (1 - 1/(kP))
        
        Returns:
            T_Λ value with minimum bound of 1e-6 for numerical stability
        """
        k = self.k
        p = self.p
        t1 = self.t1
        u = self.u
        
        # Calculate ln(U)
        ln_u = math.log(u)
        
        # Calculate denominator: 1 - 1/(kP)
        kp = k * p
        denominator = 1.0 - (1.0 / kp)
        
        # Compute T_Λ
        t_lambda = (t1 * ln_u) / denominator
        
        # Apply minimum bound for numerical stability
        epsilon = 1e-6
        t_lambda = max(epsilon, t_lambda)
        
        return t_lambda
        
    def generate_pulse(self) -> Dict[str, Any]:
        """
        Generate a T_Λ pulse with time compression
        
        Returns:
            Pulse data including t_lambda value and timing information
        """
        self.pulse_count += 1
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Compute T_Λ using the formula
        t_lambda = self.compute_t_lambda()
        
        return {
            "pulse_id": self.pulse_count,
            "timestamp": current_time,
            "elapsed": elapsed,
            "t_lambda": t_lambda,
            "k": self.k,
            "p": self.p,
            "kp": self.k * self.p
        }
    
    def get_next_pulse_delay(self) -> float:
        """
        Calculate delay until next pulse (uses T_Λ as the delay)
        
        Returns:
            Delay in seconds
        """
        return self.compute_t_lambda()
    
    def reset(self):
        """Reset pulse generator"""
        self.start_time = time.time()
        self.pulse_count = 0
