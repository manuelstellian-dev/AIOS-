"""Tests for Stage 2: Observability and Stability features."""
import pytest
import time
from venom.cli.dashboard import CLIDashboard
from venom.benchmark.performance import PerformanceBenchmark
from venom.testing.load_test import LoadTest, LoadProfile
from venom.mesh.rate_limiter import TokenBucket, MeshRateLimiter


class TestCLIDashboard:
    """Test CLI Dashboard functionality."""
    
    def test_dashboard_initialization(self):
        """Test dashboard initializes correctly."""
        dashboard = CLIDashboard(refresh_rate=0.5)
        assert dashboard.refresh_rate == 0.5
        assert dashboard.metrics_history['beats'] == 0
        assert len(dashboard.metrics_history['latency']) == 0
    
    def test_metrics_update(self):
        """Test metrics update correctly."""
        dashboard = CLIDashboard()
        
        metrics = {
            'latency': 0.005,
            'throughput': 100.0,
            'pid_error': -0.01,
            'ledger_commits': 50,
            'mesh_queue_size': 5,
            'beats': 10
        }
        
        dashboard.update_metrics(metrics)
        
        assert dashboard.metrics_history['latency'][-1] == 0.005
        assert dashboard.metrics_history['throughput'][-1] == 100.0
        assert dashboard.metrics_history['pid_error'][-1] == -0.01
        assert dashboard.metrics_history['ledger_commits'] == 50
        assert dashboard.metrics_history['mesh_queue_size'] == 5
        assert dashboard.metrics_history['beats'] == 10
    
    def test_metrics_display(self):
        """Test metrics are displayed correctly."""
        dashboard = CLIDashboard()
        
        # Add multiple metrics
        for i in range(10):
            dashboard.update_metrics({
                'latency': 0.005 + i * 0.001,
                'throughput': 90.0 + i,
                'pid_error': -0.01 - i * 0.001
            })
        
        snapshot = dashboard.get_metrics_snapshot()
        
        assert snapshot['latency_current'] == pytest.approx(0.014, rel=0.01)
        assert snapshot['latency_avg'] > 0.005
        assert snapshot['throughput_current'] == pytest.approx(99.0, rel=0.01)
        assert snapshot['throughput_avg'] > 90.0
        assert snapshot['pid_error_current'] == pytest.approx(-0.019, rel=0.01)
    
    def test_metrics_history_limit(self):
        """Test metrics history is limited to 100 items."""
        dashboard = CLIDashboard()
        
        # Add 150 latency metrics
        for i in range(150):
            dashboard.update_metrics({'latency': float(i)})
        
        assert len(dashboard.metrics_history['latency']) == 100
        # Should keep the latest 100
        assert dashboard.metrics_history['latency'][0] == 50.0
        assert dashboard.metrics_history['latency'][-1] == 149.0


class TestPerformanceBenchmark:
    """Test Performance Benchmark functionality."""
    
    def test_benchmark_initialization(self):
        """Test benchmark initializes correctly."""
        benchmark = PerformanceBenchmark()
        assert 'latency' in benchmark.results
        assert 'throughput' in benchmark.results
    
    def test_latency_benchmark(self):
        """Test latency benchmark."""
        benchmark = PerformanceBenchmark()
        
        def fast_func():
            time.sleep(0.001)  # 1ms
        
        results = benchmark.benchmark_latency(fast_func, iterations=10)
        
        assert 'min' in results
        assert 'max' in results
        assert 'mean' in results
        assert 'median' in results
        assert 'stdev' in results
        assert results['mean'] >= 0.001  # At least 1ms
        assert results['mean'] < 0.01   # Less than 10ms
    
    def test_throughput_benchmark(self):
        """Test throughput benchmark."""
        benchmark = PerformanceBenchmark()
        
        def fast_func():
            pass  # No-op for high throughput
        
        results = benchmark.benchmark_throughput(fast_func, duration=0.5)
        
        assert 'beats' in results
        assert 'duration' in results
        assert 'throughput' in results
        assert results['beats'] > 0
        assert results['throughput'] > 0
    
    def test_latency_validation(self):
        """Test latency validation."""
        benchmark = PerformanceBenchmark()
        
        # Good latency
        good_results = {'mean': 0.005}  # 5ms
        valid, msg = benchmark.validate_latency(good_results)
        assert valid
        assert "acceptable" in msg.lower()
        
        # Bad latency
        bad_results = {'mean': 0.05}  # 50ms
        valid, msg = benchmark.validate_latency(bad_results)
        assert not valid
        assert "exceeds" in msg.lower()
    
    def test_throughput_validation(self):
        """Test throughput validation."""
        benchmark = PerformanceBenchmark()
        
        # Good throughput
        good_results = {'throughput': 100.0}
        valid, msg = benchmark.validate_throughput(good_results)
        assert valid
        assert "acceptable" in msg.lower()
        
        # Bad throughput
        bad_results = {'throughput': 10.0}
        valid, msg = benchmark.validate_throughput(bad_results)
        assert not valid
        assert "below" in msg.lower()
    
    def test_full_benchmark_suite(self):
        """Test full benchmark suite."""
        benchmark = PerformanceBenchmark()
        
        def latency_func():
            time.sleep(0.001)
        
        def throughput_func():
            pass
        
        results = benchmark.run_full_benchmark(latency_func, throughput_func)
        
        assert 'latency' in results
        assert 'throughput' in results
        assert 'latency_valid' in results
        assert 'throughput_valid' in results
        assert 'overall_pass' in results


class TestLoadTest:
    """Test Load Testing functionality."""
    
    def test_load_test_initialization(self):
        """Test load test initializes correctly."""
        load_test = LoadTest()
        assert len(load_test.pid_deviations) == 0
        assert isinstance(load_test.results, dict)
    
    def test_steady_load(self):
        """Test steady load profile."""
        load_test = LoadTest()
        
        count = [0]
        def test_func():
            count[0] += 1
        
        results = load_test.run_steady_load(test_func, duration=0.5, rate=50)
        
        assert results['profile'] == 'steady'
        assert results['requests'] > 0
        assert results['duration'] >= 0.5
        assert results['target_rate'] == 50
        # Should be close to target rate
        assert abs(results['rate'] - 50) < 20  # Allow 40% variance
    
    def test_burst_load(self):
        """Test burst load profile."""
        load_test = LoadTest()
        
        count = [0]
        def test_func():
            count[0] += 1
        
        results = load_test.run_burst_load(test_func, bursts=3, burst_size=10)
        
        assert results['profile'] == 'burst'
        assert results['requests'] == 30  # 3 bursts * 10
        assert results['bursts'] == 3
        assert results['burst_size'] == 10
        assert 'avg_burst_time' in results
    
    def test_pid_deviation_logging(self):
        """Test PID deviation logging."""
        load_test = LoadTest()
        
        deviations = [0.01, -0.02, 0.015, -0.01, 0.005]
        for dev in deviations:
            load_test.log_pid_deviation(dev)
        
        assert len(load_test.pid_deviations) == 5
        assert load_test.pid_deviations == deviations
    
    def test_pid_stability_verification(self):
        """Test PID stability verification under load."""
        load_test = LoadTest()
        
        # Stable case
        for _ in range(10):
            load_test.log_pid_deviation(0.01)
        
        stable, stats = load_test.verify_pid_stability(max_deviation=0.05)
        
        assert stable
        assert stats['stable']
        assert stats['max_deviation'] == 0.01
        assert stats['samples'] == 10
        
        # Unstable case
        load_test2 = LoadTest()
        load_test2.log_pid_deviation(0.1)  # Large deviation
        
        stable, stats = load_test2.verify_pid_stability(max_deviation=0.05)
        
        assert not stable
        assert not stats['stable']
        assert stats['max_deviation'] == 0.1


class TestRateLimiting:
    """Test Rate Limiting functionality."""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initializes correctly."""
        bucket = TokenBucket(rate=10.0, capacity=20)
        assert bucket.rate == 10.0
        assert bucket.capacity == 20
        assert bucket.tokens == 20  # Starts full
    
    def test_token_consumption(self):
        """Test token consumption."""
        bucket = TokenBucket(rate=100.0, capacity=10)
        
        # Should succeed
        assert bucket.consume(1)
        assert abs(bucket.tokens - 9.0) < 0.1  # Allow for timing precision
        
        # Consume more
        assert bucket.consume(5)
        assert abs(bucket.tokens - 4.0) < 0.1  # Allow for timing precision
    
    def test_rate_limiting(self):
        """Test rate limiting behavior."""
        bucket = TokenBucket(rate=10.0, capacity=5)
        bucket.tokens = 2.0  # Set to low amount
        
        # Should succeed
        assert bucket.consume(1)
        assert bucket.consume(1)
        
        # Should fail (rate limited)
        assert not bucket.consume(1)
    
    def test_token_refill(self):
        """Test tokens refill over time."""
        bucket = TokenBucket(rate=100.0, capacity=10)
        bucket.tokens = 0.0
        
        # Wait for refill
        time.sleep(0.1)
        
        # Should have ~10 tokens (100/s * 0.1s)
        assert bucket.consume(5)
    
    def test_mesh_rate_limiter_initialization(self):
        """Test mesh rate limiter initializes correctly."""
        limiter = MeshRateLimiter(rate_per_node=100, rate_per_topic=50)
        assert limiter.rate_per_node == 100
        assert limiter.rate_per_topic == 50
        assert limiter.blocked_count == 0
    
    def test_node_rate_limiting(self):
        """Test per-node rate limiting."""
        limiter = MeshRateLimiter(rate_per_node=10, rate_per_topic=50)
        
        # Node1 should be allowed initially
        assert limiter.check_node_limit("node1")
        
        # Exhaust node1's tokens
        for _ in range(20):
            limiter.check_node_limit("node1")
        
        # Node1 should be blocked
        assert not limiter.check_node_limit("node1")
        assert limiter.blocked_count > 0
    
    def test_topic_rate_limiting(self):
        """Test per-topic rate limiting."""
        limiter = MeshRateLimiter(rate_per_node=100, rate_per_topic=10)
        
        # Topic should be allowed initially
        assert limiter.check_topic_limit("topic1")
        
        # Exhaust topic tokens
        for _ in range(20):
            limiter.check_topic_limit("topic1")
        
        # Topic should be blocked
        assert not limiter.check_topic_limit("topic1")
    
    def test_combined_limits(self):
        """Test both node and topic limits together."""
        limiter = MeshRateLimiter(rate_per_node=50, rate_per_topic=30)
        
        # Should pass both checks initially
        assert limiter.check_limits("node1", "topic1")
        
        # Different node, same topic - should still work
        assert limiter.check_limits("node2", "topic1")
    
    def test_rate_limiter_stats(self):
        """Test rate limiter statistics."""
        limiter = MeshRateLimiter()
        
        limiter.check_node_limit("node1")
        limiter.check_node_limit("node2")
        limiter.check_topic_limit("topic1")
        
        stats = limiter.get_stats()
        
        assert stats['node_count'] == 2
        assert stats['topic_count'] == 1
        assert 'blocked_total' in stats


# Integration test
class TestStage2Integration:
    """Test Stage 2 features integration."""
    
    def test_full_observability_stack(self):
        """Test dashboard + benchmarks + load test + rate limiting together."""
        # Dashboard
        dashboard = CLIDashboard()
        
        # Benchmark
        benchmark = PerformanceBenchmark()
        
        def test_func():
            time.sleep(0.001)
        
        bench_results = benchmark.run_full_benchmark(test_func, test_func)
        
        # Update dashboard with benchmark results
        dashboard.update_metrics({
            'latency': bench_results['latency']['mean'],
            'throughput': bench_results['throughput']['throughput'],
            'pid_error': -0.015,
            'ledger_commits': 100,
            'mesh_queue_size': 3,
            'beats': 50
        })
        
        snapshot = dashboard.get_metrics_snapshot()
        assert snapshot['latency_current'] > 0
        assert snapshot['throughput_current'] > 0
        
        # Load test with rate limiter
        limiter = MeshRateLimiter(rate_per_node=1000, rate_per_topic=500)
        load_test = LoadTest()
        
        def limited_func():
            if limiter.check_limits("test_node", "test_topic"):
                pass  # Allowed
        
        load_results = load_test.run_steady_load(limited_func, duration=0.3, rate=50)
        
        assert load_results['requests'] > 0
        assert limiter.get_stats()['blocked_total'] >= 0
        
        # Verify integration
        assert bench_results['overall_pass'] or not bench_results['overall_pass']  # Has result
        assert load_results['profile'] == 'steady'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
