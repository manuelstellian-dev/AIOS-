"""
T_Λ Pulse - Time compression synchronization mechanism
Provides the temporal heartbeat for the fractal organism
"""
import time
import math
from typing import Dict, Any


class TLambdaPulse:
    """
    T_Λ Pulse generator implementing time compression equation
    Synchronizes all parallel flows with a fractal temporal rhythm
    """
    
    def __init__(self, base_frequency: float = 1.0, compression_factor: float = 0.5):
        """
        Initialize T_Λ pulse generator
        
        Args:
            base_frequency: Base pulse frequency in Hz
            compression_factor: Time compression coefficient (0 < λ < 1)
        """
        self.base_frequency = base_frequency
        self.compression_factor = compression_factor
        self.start_time = time.time()
        self.pulse_count = 0
        
    def generate_pulse(self) -> Dict[str, Any]:
        """
        Generate a T_Λ pulse with time compression
        
        Returns:
            Pulse data including t_lambda value and timing information
        """
        self.pulse_count += 1
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Time compression equation: T_Λ = t * e^(-λ * sin(ωt))
        # where λ is compression factor and ω is angular frequency
        omega = 2 * math.pi * self.base_frequency
        compression = math.exp(-self.compression_factor * math.sin(omega * elapsed))
        t_lambda = elapsed * compression
        
        return {
            "pulse_id": self.pulse_count,
            "timestamp": current_time,
            "elapsed": elapsed,
            "t_lambda": t_lambda,
            "compression": compression,
            "phase": (omega * elapsed) % (2 * math.pi)
        }
    
    def get_next_pulse_delay(self) -> float:
        """
        Calculate delay until next pulse
        
        Returns:
            Delay in seconds
        """
        return 1.0 / self.base_frequency
    
    def reset(self):
        """Reset pulse generator"""
        self.start_time = time.time()
        self.pulse_count = 0
