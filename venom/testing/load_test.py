"""Load testing suite for VENOM."""
import time
import statistics
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum

class LoadProfile(Enum):
    """Load test profiles."""
    STEADY = "steady"
    BURST = "burst"

class LoadTest:
    """Stress testing with different load profiles."""
    
    def __init__(self):
        self.pid_deviations = []
        self.results = {}
    
    def run_steady_load(self, func: Callable, duration: float = 5.0, rate: float = 100) -> Dict:
        """Steady load test."""
        start = time.time()
        count = 0
        interval = 1.0 / rate
        
        while (time.time() - start) < duration:
            func()
            count += 1
            time.sleep(interval)
        
        elapsed = time.time() - start
        return {
            'profile': 'steady',
            'duration': elapsed,
            'requests': count,
            'rate': count / elapsed,
            'target_rate': rate
        }
    
    def run_burst_load(self, func: Callable, bursts: int = 5, burst_size: int = 20) -> Dict:
        """Burst load test."""
        start = time.time()
        total_requests = 0
        burst_times = []
        
        for _ in range(bursts):
            burst_start = time.time()
            for _ in range(burst_size):
                func()
                total_requests += 1
            burst_times.append(time.time() - burst_start)
            time.sleep(0.5)  # Inter-burst delay
        
        elapsed = time.time() - start
        return {
            'profile': 'burst',
            'duration': elapsed,
            'requests': total_requests,
            'bursts': bursts,
            'burst_size': burst_size,
            'avg_burst_time': statistics.mean(burst_times)
        }
    
    def log_pid_deviation(self, pid_error: float) -> None:
        """Log PID deviation during load test."""
        self.pid_deviations.append(pid_error)
    
    def verify_pid_stability(self, max_deviation: float = 0.05) -> Tuple[bool, Dict]:
        """Verify PID remained stable under load."""
        if not self.pid_deviations:
            return True, {'message': 'No PID data collected'}
        
        max_dev = max(abs(d) for d in self.pid_deviations)
        avg_dev = statistics.mean([abs(d) for d in self.pid_deviations])
        
        stable = max_dev < max_deviation
        return stable, {
            'max_deviation': max_dev,
            'avg_deviation': avg_dev,
            'threshold': max_deviation,
            'stable': stable,
            'samples': len(self.pid_deviations)
        }
