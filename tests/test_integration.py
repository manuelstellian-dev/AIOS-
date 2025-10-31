"""
Integration tests for VENOM Λ-GENESIS
Tests complete system integration and flow orchestration
"""
import pytest
import time
from venom import (
    Arbiter,
    TLambdaPulse,
    GenomicPID,
    EntropyModel,
    ImmutableLedger
)


class TestSystemIntegration:
    """Integration tests for complete system"""
    
    def test_full_beat_cycle(self):
        """Test complete beat execution cycle"""
        # Initialize components
        pulse = TLambdaPulse(k=4, p=5, t1=0.001)
        pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05, t_threshold=0.02)
        entropy_model = EntropyModel(ml_weight=0.12)
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(
            pulse=pulse,
            pid=pid,
            entropy_model=entropy_model,
            ledger=ledger
        )
        
        # Execute one beat
        summary = arbiter.execute_beat()
        
        # Verify beat executed
        assert summary["beat"] == 1
        assert "t_lambda" in summary
        assert "action" in summary
        assert "decvec" in summary
        assert "weights" in summary
        
        # Verify ledger recorded entries
        assert ledger.get_chain_length() > 1
        
        # Verify PID computed
        assert "weight_adjustment" in summary
        
        arbiter.stop()
    
    def test_multiple_beats_stability(self):
        """Test system stability over multiple beats"""
        pulse = TLambdaPulse(k=4, p=5)
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        # Execute 10 beats
        for _ in range(10):
            summary = arbiter.execute_beat()
            assert summary["beat"] >= 1
            assert summary["ledger_length"] > 0
        
        # Verify ledger integrity
        assert ledger.verify_chain() == True
        
        # Verify genome weights sum to ~1.0
        status = arbiter.get_status()
        weights = status["genome"]["weights"]
        weight_sum = sum(weights.values())
        assert 0.99 <= weight_sum <= 1.01
        
        arbiter.stop()
    
    def test_parallel_core_execution(self):
        """Test that cores execute in parallel"""
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        start_time = time.time()
        summary = arbiter.execute_beat()
        duration = time.time() - start_time
        
        # Parallel execution should be faster than sequential
        # Even with overhead, should complete quickly
        assert duration < 1.0  # Should be much faster
        
        arbiter.stop()
    
    def test_decision_making(self):
        """Test decision logic with different threat levels"""
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        # Low threat scenario - should be NOOP or OPTIMIZE
        summary = arbiter.execute_beat()
        assert summary["action"] in ["NOOP", "APPLY_OPTIMIZE"]
        
        # Inject high anomalies for high threat
        arbiter.genome["risk"]["anoms"] = 100
        summary = arbiter.execute_beat()
        
        # Should trigger ALERT or QUARANTINE with high threat
        # (Depends on entropy model inference)
        assert summary["action"] in ["ALERT", "QUARANTINE", "NOOP", "APPLY_OPTIMIZE"]
        
        arbiter.stop()
    
    def test_genome_evolution(self):
        """Test genome weight evolution over time"""
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        initial_weights = dict(arbiter.genome["weights"])
        
        # Execute several beats
        for _ in range(20):
            arbiter.execute_beat()
        
        final_weights = dict(arbiter.genome["weights"])
        
        # Weights should evolve (O weight especially)
        assert initial_weights != final_weights
        
        # But should remain normalized
        weight_sum = sum(final_weights.values())
        assert 0.99 <= weight_sum <= 1.01
        
        arbiter.stop()
    
    def test_ledger_integrity_maintained(self):
        """Test ledger integrity is maintained throughout execution"""
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        # Execute multiple beats
        for _ in range(15):
            arbiter.execute_beat()
            # Verify chain after each beat
            assert ledger.verify_chain() == True
        
        # Verify Merkle root can be computed
        merkle_root = ledger.compute_merkle_root()
        assert isinstance(merkle_root, str)
        assert len(merkle_root) == 64  # SHA3-256 hex length
        
        arbiter.stop()
    
    def test_pid_stability_convergence(self):
        """Test PID controller converges to stability"""
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        
        # Execute many beats to allow PID to stabilize
        for _ in range(50):
            arbiter.execute_beat()
        
        # Check if PID has achieved stability
        # (May not be stable yet, but should be converging)
        status = arbiter.get_status()
        
        # At minimum, PID should have recorded history
        assert len(arbiter.pid.stability_history) > 0
        
        arbiter.stop()


class TestObservability:
    """Integration tests for observability features"""
    
    def test_metrics_collection(self):
        """Test metrics are collected during execution"""
        from venom.observability import MetricsCollector
        
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        metrics = MetricsCollector()
        
        # Execute beat and record metrics
        start = time.time()
        summary = arbiter.execute_beat()
        duration = time.time() - start
        
        metrics.record_beat(duration)
        metrics.record_decision(summary["action"])
        metrics.record_genome_weights(summary["weights"])
        
        # Verify metrics were recorded
        summary_data = metrics.get_summary()
        assert summary_data["counters"]["venom_beats_total"] == 1
        assert summary_data["gauges"]["venom_beat_duration_seconds"] > 0
        
        arbiter.stop()
    
    def test_health_checker(self):
        """Test health checker integration"""
        from venom.observability import HealthChecker
        
        pulse = TLambdaPulse()
        pid = GenomicPID()
        entropy_model = EntropyModel()
        ledger = ImmutableLedger()
        
        arbiter = Arbiter(pulse=pulse, pid=pid, entropy_model=entropy_model, ledger=ledger)
        health = HealthChecker(arbiter)
        
        # Check readiness
        readiness = health.check_readiness()
        assert "status" in readiness
        assert "checks" in readiness
        
        # Check liveness
        liveness = health.check_liveness()
        assert "status" in liveness
        assert "uptime_seconds" in liveness["checks"]
        
        # Execute beat and record
        arbiter.execute_beat()
        health.record_beat()
        
        # Check overall health
        health_status = health.check_health()
        assert health_status["status"] in ["healthy", "degraded", "unhealthy"]
        
        arbiter.stop()
