"""
Tests for HealthMonitor
"""
import pytest
import time
import os
from venom.observability import HealthMonitor


class TestHealthMonitor:
    """Test suite for HealthMonitor"""
    
    def test_register_health_check(self):
        """Test registering and unregistering health checks"""
        monitor = HealthMonitor()
        
        # Register a check
        def always_pass():
            return True
        
        monitor.register_check("test_check", always_pass, critical=True)
        
        # Run checks
        results = monitor.run_checks()
        assert "test_check" in results
        assert results["test_check"]["status"] == "pass"
        assert results["test_check"]["critical"] is True
        
        # Unregister
        assert monitor.unregister_check("test_check") is True
        assert monitor.unregister_check("test_check") is False  # Already removed
        
        # Check no longer exists
        results = monitor.run_checks()
        assert "test_check" not in results
    
    def test_system_checks(self):
        """Test built-in system health checks"""
        monitor = HealthMonitor()
        
        # Test CPU check
        cpu_healthy = monitor.check_cpu_usage(threshold=99.0)
        assert isinstance(cpu_healthy, bool)
        # Should pass with high threshold
        assert cpu_healthy is True
        
        # Test memory check
        mem_healthy = monitor.check_memory_usage(threshold=99.0)
        assert isinstance(mem_healthy, bool)
        # Should pass with high threshold
        assert mem_healthy is True
        
        # Test disk check
        disk_healthy = monitor.check_disk_usage(threshold=99.0)
        assert isinstance(disk_healthy, bool)
        # Should pass with high threshold
        assert disk_healthy is True
        
        # Test process check
        current_pid = os.getpid()
        assert monitor.check_process_alive(current_pid) is True
        assert monitor.check_process_alive(999999) is False  # Non-existent PID
    
    def test_health_status_aggregation(self):
        """Test health status aggregation logic"""
        monitor = HealthMonitor()
        
        # All checks pass
        monitor.register_check("check1", lambda: True, critical=False)
        monitor.register_check("check2", lambda: True, critical=False)
        status = monitor.get_health_status()
        assert status == "healthy"
        
        # Non-critical failure
        monitor.register_check("check3", lambda: False, critical=False)
        status = monitor.get_health_status()
        assert status == "degraded"
        
        # Critical failure
        monitor.register_check("check4", lambda: False, critical=True)
        status = monitor.get_health_status()
        assert status == "unhealthy"
    
    def test_check_history(self):
        """Test health check history tracking"""
        monitor = HealthMonitor()
        
        # Register a check
        counter = {"value": 0}
        def alternating_check():
            counter["value"] += 1
            return counter["value"] % 2 == 0
        
        monitor.register_check("alternating", alternating_check)
        
        # Run checks multiple times
        for _ in range(5):
            monitor.run_checks()
        
        # Get history
        history = monitor.get_check_history("alternating", limit=5)
        assert len(history) == 5
        
        # Verify history contains status
        for entry in history:
            assert "status" in entry
            assert entry["status"] in ["pass", "fail"]
            assert "timestamp" in entry
        
        # Test non-existent check
        empty_history = monitor.get_check_history("nonexistent")
        assert len(empty_history) == 0
    
    def test_background_monitoring(self):
        """Test background monitoring thread"""
        monitor = HealthMonitor(check_interval=1)
        
        # Register a check
        check_count = {"value": 0}
        def counting_check():
            check_count["value"] += 1
            return True
        
        monitor.register_check("counter", counting_check)
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor._monitoring is True
        
        # Wait for at least 2 checks (2+ seconds)
        time.sleep(2.5)
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor._monitoring is False
        
        # Verify checks were run multiple times
        assert check_count["value"] >= 2
        
        # Verify history was recorded
        history = monitor.get_check_history("counter")
        assert len(history) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
