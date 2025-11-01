"""
Tests for MetricsCollector
"""
import pytest
from venom.observability import MetricsCollector


class TestMetricsCollector:
    """Test suite for MetricsCollector"""
    
    def test_counter_metrics(self):
        """Test counter metric operations"""
        collector = MetricsCollector()
        
        # Test increment
        collector.increment_counter("test_counter", 5.0)
        assert collector.get_counter("test_counter") == 5.0
        
        # Test increment with default value
        collector.increment_counter("test_counter")
        assert collector.get_counter("test_counter") == 6.0
        
        # Test with labels
        collector.increment_counter("test_counter_labeled", 3.0, labels={"env": "test"})
        assert collector.get_counter("test_counter_labeled", labels={"env": "test"}) == 3.0
        
        # Test non-existent counter
        assert collector.get_counter("nonexistent") == 0.0
    
    def test_gauge_metrics(self):
        """Test gauge metric operations"""
        collector = MetricsCollector()
        
        # Test set gauge
        collector.set_gauge("test_gauge", 42.0)
        assert collector.get_gauge("test_gauge") == 42.0
        
        # Test update gauge
        collector.set_gauge("test_gauge", 100.0)
        assert collector.get_gauge("test_gauge") == 100.0
        
        # Test with labels
        collector.set_gauge("test_gauge_labeled", 25.5, labels={"region": "us-east"})
        assert collector.get_gauge("test_gauge_labeled", labels={"region": "us-east"}) == 25.5
        
        # Test non-existent gauge
        assert collector.get_gauge("nonexistent") == 0.0
    
    def test_histogram_metrics(self):
        """Test histogram metric operations"""
        collector = MetricsCollector()
        
        # Add observations
        collector.observe_histogram("test_histogram", 1.0)
        collector.observe_histogram("test_histogram", 2.0)
        collector.observe_histogram("test_histogram", 3.0)
        collector.observe_histogram("test_histogram", 4.0)
        collector.observe_histogram("test_histogram", 5.0)
        
        # Get stats
        stats = collector.get_histogram_stats("test_histogram")
        assert stats["count"] == 5
        assert stats["sum"] == 15.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["avg"] == 3.0
        
        # Test empty histogram
        empty_stats = collector.get_histogram_stats("nonexistent")
        assert empty_stats["count"] == 0
        assert empty_stats["sum"] == 0.0
    
    def test_summary_metrics(self):
        """Test summary metric operations with percentiles"""
        collector = MetricsCollector()
        
        # Add observations
        for i in range(1, 101):
            collector.observe_summary("test_summary", float(i))
        
        # Get stats
        stats = collector.get_summary_stats("test_summary")
        assert stats["count"] == 100
        assert stats["sum"] == 5050.0
        assert stats["p50"] == 50.0
        assert stats["p90"] == 90.0
        assert stats["p95"] == 95.0
        assert stats["p99"] == 99.0
        
        # Test empty summary
        empty_stats = collector.get_summary_stats("nonexistent")
        assert empty_stats["count"] == 0
        assert empty_stats["p50"] == 0.0
    
    def test_prometheus_export(self):
        """Test Prometheus format export"""
        collector = MetricsCollector()
        
        # Add some metrics
        collector.increment_counter("requests_total", 100)
        collector.set_gauge("temperature", 72.5)
        collector.observe_histogram("request_duration", 0.5)
        
        # Export
        export = collector.export_prometheus()
        
        # Verify format
        assert isinstance(export, str)
        assert "requests_total" in export
        assert "temperature" in export
        assert "request_duration" in export
        assert "# TYPE" in export
        
        # Test JSON export
        json_export = collector.export_json()
        assert isinstance(json_export, dict)
        assert "counters" in json_export
        assert "gauges" in json_export
        assert "histograms" in json_export
        assert "summaries" in json_export
        
        # Test reset
        collector.reset_metrics()
        # Should still have initialized metrics but reset to defaults
        assert collector.get_counter("requests_total") == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
