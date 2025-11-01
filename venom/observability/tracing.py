"""
Distributed Tracing for VENOM Λ-GENESIS
OpenTelemetry-style distributed tracing with context propagation
"""
import time
import uuid
import threading
from typing import Dict, Any, List, Optional
from collections import deque
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DistributedTracer:
    """
    Distributed tracer with span management and context propagation
    OpenTelemetry-compatible tracing implementation
    """
    
    def __init__(self, service_name: str = 'venom'):
        """
        Initialize distributed tracer
        
        Args:
            service_name: Name of the service for tracing
        """
        self.service_name = service_name
        self._spans: Dict[str, Dict[str, Any]] = {}
        self._traces: Dict[str, List[str]] = {}  # trace_id -> [span_ids]
        self._span_buffer = deque(maxlen=10000)  # Circular buffer for spans
        self._lock = threading.Lock()
    
    def start_span(self, name: str, parent_span_id: Optional[str] = None) -> str:
        """
        Start a new span
        
        Args:
            name: Name of the span/operation
            parent_span_id: Optional parent span ID
            
        Returns:
            span_id for the new span
        """
        span_id = str(uuid.uuid4())
        
        with self._lock:
            # Determine trace_id
            if parent_span_id and parent_span_id in self._spans:
                trace_id = self._spans[parent_span_id]["trace_id"]
            else:
                trace_id = str(uuid.uuid4())
            
            span = {
                "span_id": span_id,
                "trace_id": trace_id,
                "parent_span_id": parent_span_id,
                "name": name,
                "service_name": self.service_name,
                "start_time": time.time(),
                "end_time": None,
                "status": "in_progress",
                "attributes": {},
                "events": []
            }
            
            self._spans[span_id] = span
            
            # Track spans by trace
            if trace_id not in self._traces:
                self._traces[trace_id] = []
            self._traces[trace_id].append(span_id)
        
        return span_id
    
    def end_span(self, span_id: str, status: str = 'ok', error: Optional[str] = None) -> None:
        """
        End a span
        
        Args:
            span_id: ID of the span to end
            status: Status ('ok', 'error', 'cancelled')
            error: Optional error message
        """
        with self._lock:
            if span_id not in self._spans:
                logger.warning(f"Span {span_id} not found")
                return
            
            span = self._spans[span_id]
            span["end_time"] = time.time()
            span["status"] = status
            span["duration"] = span["end_time"] - span["start_time"]
            
            if error:
                span["error"] = error
            
            # Add to buffer for export
            self._span_buffer.append(dict(span))
    
    def add_span_attribute(self, span_id: str, key: str, value: Any) -> None:
        """
        Add attribute to a span
        
        Args:
            span_id: ID of the span
            key: Attribute key
            value: Attribute value
        """
        with self._lock:
            if span_id not in self._spans:
                logger.warning(f"Span {span_id} not found")
                return
            
            self._spans[span_id]["attributes"][key] = value
    
    def add_span_event(self, span_id: str, event_name: str, attributes: Optional[Dict] = None) -> None:
        """
        Add event to a span
        
        Args:
            span_id: ID of the span
            event_name: Name of the event
            attributes: Optional event attributes
        """
        with self._lock:
            if span_id not in self._spans:
                logger.warning(f"Span {span_id} not found")
                return
            
            event = {
                "name": event_name,
                "timestamp": time.time(),
                "attributes": attributes or {}
            }
            
            self._spans[span_id]["events"].append(event)
    
    def inject_context(self, span_id: str) -> Dict[str, str]:
        """
        Inject trace context for propagation (W3C Trace Context format)
        
        Args:
            span_id: ID of the current span
            
        Returns:
            Dictionary with trace context headers
        """
        with self._lock:
            if span_id not in self._spans:
                return {}
            
            span = self._spans[span_id]
            trace_id = span["trace_id"]
            
            # W3C Trace Context format
            # traceparent: version-trace_id-parent_id-trace_flags
            traceparent = f"00-{trace_id.replace('-', '')[:32]}-{span_id.replace('-', '')[:16]}-01"
            
            return {
                "traceparent": traceparent,
                "tracestate": f"venom={self.service_name}"
            }
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Extract trace context from headers
        
        Args:
            headers: Dictionary of HTTP headers
            
        Returns:
            parent_span_id if found, None otherwise
        """
        traceparent = headers.get("traceparent", headers.get("Traceparent"))
        
        if not traceparent:
            return None
        
        try:
            # Parse W3C Trace Context format: version-trace_id-parent_id-trace_flags
            parts = traceparent.split("-")
            if len(parts) >= 3:
                parent_id = parts[2]
                # Convert back to UUID format
                return f"{parent_id[:8]}-{parent_id[8:12]}-{parent_id[12:16]}-{parent_id[16:20]}-{parent_id[20:32]}"
        except Exception as e:
            logger.error(f"Failed to extract context: {e}")
        
        return None
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """
        Get all spans for a trace
        
        Args:
            trace_id: ID of the trace
            
        Returns:
            List of span dictionaries
        """
        with self._lock:
            if trace_id not in self._traces:
                return []
            
            span_ids = self._traces[trace_id]
            spans = []
            
            for span_id in span_ids:
                if span_id in self._spans:
                    spans.append(dict(self._spans[span_id]))
                else:
                    # Check buffer for completed spans
                    for buffered_span in self._span_buffer:
                        if buffered_span["span_id"] == span_id:
                            spans.append(buffered_span)
                            break
            
            return spans
    
    def get_span(self, span_id: str) -> Optional[Dict]:
        """
        Get a specific span
        
        Args:
            span_id: ID of the span
            
        Returns:
            Span dictionary or None
        """
        with self._lock:
            if span_id in self._spans:
                return dict(self._spans[span_id])
            
            # Check buffer
            for span in self._span_buffer:
                if span["span_id"] == span_id:
                    return span
        
        return None
    
    def export_traces(self, format: str = 'json') -> str:
        """
        Export traces in specified format
        
        Args:
            format: Export format ('json' or 'opentelemetry')
            
        Returns:
            Formatted trace data as string
        """
        import json
        
        with self._lock:
            if format == 'json':
                # Export active spans and buffer
                active_spans = [dict(span) for span in self._spans.values()]
                buffered_spans = list(self._span_buffer)
                
                export_data = {
                    "service_name": self.service_name,
                    "active_spans": active_spans,
                    "completed_spans": buffered_spans
                }
                
                return json.dumps(export_data, indent=2)
            
            elif format == 'opentelemetry':
                # OpenTelemetry format
                resource_spans = []
                
                for trace_id, span_ids in self._traces.items():
                    spans_data = []
                    
                    for span_id in span_ids:
                        span = self._spans.get(span_id)
                        if span:
                            spans_data.append({
                                "traceId": trace_id.replace('-', ''),
                                "spanId": span_id.replace('-', '')[:16],
                                "parentSpanId": span.get("parent_span_id", "").replace('-', '')[:16] if span.get("parent_span_id") else None,
                                "name": span["name"],
                                "kind": "SPAN_KIND_INTERNAL",
                                "startTimeUnixNano": int(span["start_time"] * 1e9),
                                "endTimeUnixNano": int(span["end_time"] * 1e9) if span["end_time"] else None,
                                "attributes": [
                                    {"key": k, "value": {"stringValue": str(v)}}
                                    for k, v in span["attributes"].items()
                                ],
                                "status": {"code": 1 if span["status"] == "ok" else 2}
                            })
                    
                    if spans_data:
                        resource_spans.append({
                            "resource": {
                                "attributes": [
                                    {"key": "service.name", "value": {"stringValue": self.service_name}}
                                ]
                            },
                            "scopeSpans": [{
                                "scope": {"name": "venom.tracer"},
                                "spans": spans_data
                            }]
                        })
                
                return json.dumps({"resourceSpans": resource_spans}, indent=2)
            
            else:
                raise ValueError(f"Unknown format: {format}")
    
    @contextmanager
    def trace_operation(self, operation_name: str, parent_span_id: Optional[str] = None):
        """
        Context manager for tracing operations
        
        Args:
            operation_name: Name of the operation to trace
            parent_span_id: Optional parent span ID
            
        Yields:
            span_id for the operation
        """
        span_id = self.start_span(operation_name, parent_span_id)
        
        try:
            yield span_id
            self.end_span(span_id, status='ok')
        except Exception as e:
            self.end_span(span_id, status='error', error=str(e))
            raise
