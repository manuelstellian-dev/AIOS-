"""
Tests for DistributedTracer
"""
import pytest
import time
from venom.observability import DistributedTracer


class TestDistributedTracer:
    """Test suite for DistributedTracer"""
    
    def test_start_end_span(self):
        """Test basic span creation and ending"""
        tracer = DistributedTracer(service_name="test-service")
        
        # Start a span
        span_id = tracer.start_span("test-operation")
        assert span_id is not None
        
        # Get span
        span = tracer.get_span(span_id)
        assert span is not None
        assert span["name"] == "test-operation"
        assert span["service_name"] == "test-service"
        assert span["status"] == "in_progress"
        assert span["start_time"] > 0
        assert span["end_time"] is None
        
        # Add attribute
        tracer.add_span_attribute(span_id, "user_id", "123")
        span = tracer.get_span(span_id)
        assert span["attributes"]["user_id"] == "123"
        
        # Add event
        tracer.add_span_event(span_id, "cache_miss", {"key": "user:123"})
        span = tracer.get_span(span_id)
        assert len(span["events"]) == 1
        assert span["events"][0]["name"] == "cache_miss"
        
        # End span
        tracer.end_span(span_id, status="ok")
        span = tracer.get_span(span_id)
        assert span["status"] == "ok"
        assert span["end_time"] > 0
        assert span["duration"] > 0
    
    def test_parent_child_spans(self):
        """Test parent-child span relationships"""
        tracer = DistributedTracer()
        
        # Start parent span
        parent_id = tracer.start_span("parent-operation")
        parent_span = tracer.get_span(parent_id)
        parent_trace_id = parent_span["trace_id"]
        
        # Start child span
        child_id = tracer.start_span("child-operation", parent_span_id=parent_id)
        child_span = tracer.get_span(child_id)
        
        # Verify relationship
        assert child_span["parent_span_id"] == parent_id
        assert child_span["trace_id"] == parent_trace_id  # Same trace
        
        # Get entire trace
        trace_spans = tracer.get_trace(parent_trace_id)
        assert len(trace_spans) == 2
        
        # End spans
        tracer.end_span(child_id)
        tracer.end_span(parent_id)
    
    def test_context_propagation(self):
        """Test W3C trace context propagation"""
        tracer = DistributedTracer()
        
        # Start a span
        span_id = tracer.start_span("service-a")
        
        # Inject context
        headers = tracer.inject_context(span_id)
        assert "traceparent" in headers
        assert "tracestate" in headers
        
        # Verify traceparent format (version-trace_id-parent_id-flags)
        traceparent = headers["traceparent"]
        parts = traceparent.split("-")
        assert len(parts) == 4
        assert parts[0] == "00"  # Version
        
        # Extract context
        extracted_span_id = tracer.extract_context(headers)
        assert extracted_span_id is not None
        
        # Test with empty headers
        assert tracer.extract_context({}) is None
    
    def test_trace_retrieval(self):
        """Test trace and span retrieval"""
        tracer = DistributedTracer()
        
        # Create a trace with multiple spans
        root_id = tracer.start_span("root")
        root_span = tracer.get_span(root_id)
        trace_id = root_span["trace_id"]
        
        child1_id = tracer.start_span("child1", parent_span_id=root_id)
        child2_id = tracer.start_span("child2", parent_span_id=root_id)
        
        # Get trace
        trace_spans = tracer.get_trace(trace_id)
        assert len(trace_spans) == 3
        
        # End all spans
        tracer.end_span(child1_id)
        tracer.end_span(child2_id)
        tracer.end_span(root_id)
        
        # Retrieve specific span
        span = tracer.get_span(child1_id)
        assert span["name"] == "child1"
        
        # Test non-existent trace
        empty_trace = tracer.get_trace("nonexistent-trace-id")
        assert len(empty_trace) == 0
        
        # Test non-existent span
        assert tracer.get_span("nonexistent-span-id") is None
    
    def test_trace_decorator(self):
        """Test trace_operation context manager"""
        tracer = DistributedTracer()
        
        # Test successful operation
        with tracer.trace_operation("database-query") as span_id:
            assert span_id is not None
            tracer.add_span_attribute(span_id, "query", "SELECT * FROM users")
            time.sleep(0.01)  # Simulate work
        
        # Verify span was created and ended
        span = tracer.get_span(span_id)
        assert span is not None
        assert span["status"] == "ok"
        assert span["duration"] > 0
        
        # Test operation with error
        try:
            with tracer.trace_operation("failing-operation") as span_id:
                tracer.add_span_attribute(span_id, "attempt", 1)
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify error was recorded
        span = tracer.get_span(span_id)
        assert span["status"] == "error"
        assert "error" in span
        assert "Test error" in span["error"]
    
    def test_export_traces(self):
        """Test trace export in multiple formats"""
        tracer = DistributedTracer(service_name="export-test")
        
        # Create some spans
        span_id = tracer.start_span("operation1")
        tracer.add_span_attribute(span_id, "key", "value")
        tracer.end_span(span_id)
        
        # Export as JSON
        json_export = tracer.export_traces(format='json')
        assert isinstance(json_export, str)
        assert "export-test" in json_export
        assert "operation1" in json_export
        
        # Export as OpenTelemetry format
        otel_export = tracer.export_traces(format='opentelemetry')
        assert isinstance(otel_export, str)
        assert "resourceSpans" in otel_export
        assert "service.name" in otel_export
        
        # Test invalid format
        with pytest.raises(ValueError):
            tracer.export_traces(format='invalid')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
