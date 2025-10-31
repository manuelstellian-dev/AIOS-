"""Performance benchmarks for VENOM."""
import time
import statistics
from typing import Dict, List, Tuple, Optional

class PerformanceBenchmark:
    """Standard performance benchmarks."""
    
    # Acceptable ranges
    LATENCY_MAX = 0.01  # 10ms max
    THROUGHPUT_MIN = 50  # 50 beats/s min
    
    def __init__(self):
        self.results = {'latency': [], 'throughput': []}
    
    def benchmark_latency(self, func, iterations: int = 100) -> Dict[str, float]:
        """Benchmark latency."""
        latencies = []
        for _ in range(iterations):
            start = time.time()
            func()
            latencies.append(time.time() - start)
        
        return {
            'min': min(latencies),
            'max': max(latencies),
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        }
    
    def benchmark_throughput(self, func, duration: float = 1.0) -> Dict[str, float]:
        """Benchmark throughput."""
        start = time.time()
        count = 0
        while (time.time() - start) < duration:
            func()
            count += 1
        elapsed = time.time() - start
        return {
            'beats': count,
            'duration': elapsed,
            'throughput': count / elapsed
        }
    
    def validate_latency(self, results: Dict[str, float]) -> Tuple[bool, str]:
        """Validate latency is acceptable."""
        if results['mean'] > self.LATENCY_MAX:
            return False, f"Latency {results['mean']:.6f}s exceeds max {self.LATENCY_MAX}s"
        return True, "Latency acceptable"
    
    def validate_throughput(self, results: Dict[str, float]) -> Tuple[bool, str]:
        """Validate throughput is acceptable."""
        if results['throughput'] < self.THROUGHPUT_MIN:
            return False, f"Throughput {results['throughput']:.2f} below min {self.THROUGHPUT_MIN}"
        return True, "Throughput acceptable"
    
    def run_full_benchmark(self, latency_func, throughput_func) -> Dict[str, any]:
        """Run complete benchmark suite."""
        latency_results = self.benchmark_latency(latency_func)
        throughput_results = self.benchmark_throughput(throughput_func)
        
        latency_ok, latency_msg = self.validate_latency(latency_results)
        throughput_ok, throughput_msg = self.validate_throughput(throughput_results)
        
        return {
            'latency': latency_results,
            'throughput': throughput_results,
            'latency_valid': latency_ok,
            'latency_message': latency_msg,
            'throughput_valid': throughput_ok,
            'throughput_message': throughput_msg,
            'overall_pass': latency_ok and throughput_ok
        }
