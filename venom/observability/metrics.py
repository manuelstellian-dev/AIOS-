"""
Prometheus Metrics Collection for VENOM Λ-GENESIS
Exports system metrics for monitoring and alerting
"""
import time
from typing import Dict, Any, Optional
from collections import defaultdict
import threading
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and aggregates metrics for Prometheus export
    Thread-safe metrics collection with counters, gauges, and histograms
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._summaries: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        
        # Initialize core metrics
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize core VENOM metrics"""
        # Beat metrics
        self._counters["venom_beats_total"] = 0
        self._gauges["venom_beat_duration_seconds"] = 0
        
        # Core execution metrics
        self._counters["venom_core_executions_total"] = 0
        self._gauges["venom_cores_active"] = 0
        
        # Decision metrics
        self._counters["venom_decisions_total"] = 0
        self._counters["venom_quarantine_total"] = 0
        self._counters["venom_alert_total"] = 0
        
        # PID metrics
        self._gauges["venom_pid_error"] = 0
        self._gauges["venom_pid_integral"] = 0
        self._gauges["venom_pid_output"] = 0
        self._gauges["venom_genome_weight_o"] = 0.35
        
        # Ledger metrics
        self._counters["venom_ledger_entries_total"] = 0
        self._gauges["venom_ledger_chain_length"] = 1
        
        # Threat metrics
        self._gauges["venom_threat_score"] = 0
        self._gauges["venom_entropy_level"] = 0
        
        # P2P Mesh metrics
        self._gauges["venom_mesh_peers_connected"] = 0
        self._gauges["venom_mesh_queue_length"] = 0
        self._counters["venom_mesh_messages_sent_total"] = 0
        self._counters["venom_mesh_messages_received_total"] = 0
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            self._counters[metric_key] += value
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get counter value"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            return self._counters.get(metric_key, 0.0)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            self._gauges[metric_key] = value
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            return self._gauges.get(metric_key, 0.0)
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Add observation to histogram"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            self._histograms[metric_key].append(value)
            
            # Keep only last 1000 observations
            if len(self._histograms[metric_key]) > 1000:
                self._histograms[metric_key] = self._histograms[metric_key][-1000:]
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict:
        """Get histogram statistics"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            values = self._histograms.get(metric_key, [])
            
            if not values:
                return {"count": 0, "sum": 0.0, "min": 0.0, "max": 0.0, "avg": 0.0}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            }
    
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Add observation to summary"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            self._summaries[metric_key].append(value)
            
            # Keep only last 1000 observations
            if len(self._summaries[metric_key]) > 1000:
                self._summaries[metric_key] = self._summaries[metric_key][-1000:]
    
    def get_summary_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict:
        """Get summary statistics with percentiles"""
        with self._lock:
            metric_key = self._format_metric_name(name, labels)
            values = self._summaries.get(metric_key, [])
            
            if not values:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "p50": 0.0,
                    "p90": 0.0,
                    "p95": 0.0,
                    "p99": 0.0
                }
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            def percentile(p: float) -> float:
                idx = int(count * p / 100) - 1
                if idx < 0:
                    idx = 0
                if idx >= count:
                    idx = count - 1
                return sorted_values[idx]
            
            return {
                "count": count,
                "sum": sum(values),
                "p50": percentile(50),
                "p90": percentile(90),
                "p95": percentile(95),
                "p99": percentile(99)
            }
    
    def _format_metric_name(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Format metric name with labels"""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def record_beat(self, duration: float):
        """Record beat execution"""
        self.increment_counter("venom_beats_total")
        self.set_gauge("venom_beat_duration_seconds", duration)
        self.observe_histogram("venom_beat_duration_histogram", duration)
    
    def record_core_execution(self, core_name: str, duration: float):
        """Record core execution"""
        self.increment_counter("venom_core_executions_total", labels={"core": core_name})
        self.observe_histogram(f"venom_core_duration_seconds", duration, labels={"core": core_name})
    
    def record_decision(self, action: str):
        """Record decision action"""
        self.increment_counter("venom_decisions_total", labels={"action": action})
        
        if action == "QUARANTINE":
            self.increment_counter("venom_quarantine_total")
        elif action == "ALERT":
            self.increment_counter("venom_alert_total")
    
    def record_pid_state(self, error: float, integral: float, output: float):
        """Record PID controller state"""
        self.set_gauge("venom_pid_error", error)
        self.set_gauge("venom_pid_integral", integral)
        self.set_gauge("venom_pid_output", output)
    
    def record_genome_weights(self, weights: Dict[str, float]):
        """Record genome weights"""
        for name, value in weights.items():
            self.set_gauge(f"venom_genome_weight_{name.lower()}", value)
    
    def record_threat(self, threat_score: float, entropy_level: float):
        """Record threat metrics"""
        self.set_gauge("venom_threat_score", threat_score)
        self.set_gauge("venom_entropy_level", entropy_level)
    
    def record_ledger_entry(self, chain_length: int):
        """Record ledger entry"""
        self.increment_counter("venom_ledger_entries_total")
        self.set_gauge("venom_ledger_chain_length", chain_length)
    
    def record_mesh_metrics(self, peers: int, queue_length: int):
        """Record P2P mesh metrics"""
        self.set_gauge("venom_mesh_peers_connected", peers)
        self.set_gauge("venom_mesh_queue_length", queue_length)
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        with self._lock:
            # Export counters
            for name, value in sorted(self._counters.items()):
                lines.append(f"# TYPE {name.split('{')[0]} counter")
                lines.append(f"{name} {value}")
            
            # Export gauges
            for name, value in sorted(self._gauges.items()):
                lines.append(f"# TYPE {name.split('{')[0]} gauge")
                lines.append(f"{name} {value}")
            
            # Export histograms (simplified - just count and sum)
            for name, values in sorted(self._histograms.items()):
                base_name = name.split('{')[0]
                labels = name[len(base_name):] if '{' in name else ""
                
                lines.append(f"# TYPE {base_name} histogram")
                lines.append(f"{base_name}_count{labels} {len(values)}")
                lines.append(f"{base_name}_sum{labels} {sum(values)}")
                
                if values:
                    lines.append(f"{base_name}_bucket{{le=\"+Inf\"{labels[1:] if labels else ''} {len(values)}")
        
        return "\n".join(lines) + "\n"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histogram_counts": {k: len(v) for k, v in self._histograms.items()}
            }
    
    def export_json(self) -> Dict:
        """Export metrics in JSON format"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: {
                        "count": len(values),
                        "sum": sum(values),
                        "values": values[-100:]  # Last 100 values
                    }
                    for name, values in self._histograms.items()
                },
                "summaries": {
                    name: self._calculate_percentiles(values)
                    for name, values in self._summaries.items()
                }
            }
    
    def _calculate_percentiles(self, values: list) -> Dict:
        """Calculate percentiles for summary"""
        if not values:
            return {"count": 0, "sum": 0.0, "p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        def percentile(p: float) -> float:
            idx = int(count * p / 100) - 1
            if idx < 0:
                idx = 0
            if idx >= count:
                idx = count - 1
            return sorted_values[idx]
        
        return {
            "count": count,
            "sum": sum(values),
            "p50": percentile(50),
            "p90": percentile(90),
            "p95": percentile(95),
            "p99": percentile(99)
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics to initial state"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._summaries.clear()
            self._initialize_metrics()


class MetricsServer:
    """
    Simple HTTP server for Prometheus metrics scraping
    Runs on port 8000 by default
    """
    
    def __init__(self, collector: MetricsCollector, port: int = 8000, host: str = "0.0.0.0"):
        """
        Initialize metrics server
        
        Args:
            collector: MetricsCollector instance
            port: Port to listen on (default 8000)
            host: Host to bind to (default 0.0.0.0)
        """
        self.collector = collector
        self.port = port
        self.host = host
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start metrics server"""
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        logger.info(f"Metrics server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop metrics server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
        logger.info("Metrics server stopped")
    
    def _run_server(self):
        """Run simple HTTP server"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            collector = self.collector
            
            class MetricsHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/metrics":
                        metrics = collector.export_prometheus()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(metrics.encode())
                    elif self.path == "/health":
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    # Suppress default logging
                    pass
            
            server = HTTPServer((self.host, self.port), MetricsHandler)
            server.timeout = 1.0
            
            while self.running:
                server.handle_request()
        
        except Exception as e:
            logger.error(f"Metrics server error: {e}")
