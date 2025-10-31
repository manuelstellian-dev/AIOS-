"""CLI Dashboard for real-time VENOM monitoring."""
import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class CLIDashboard:
    """Interactive CLI dashboard."""
    def __init__(self, arbiter=None, refresh_rate: float = 0.5):
        if not RICH_AVAILABLE:
            raise ImportError("rich library required for dashboard")
        self.arbiter = arbiter
        self.refresh_rate = refresh_rate
        self.console = Console()
        self.metrics_history = {
            'latency': [], 'throughput': [], 'pid_error': [],
            'ledger_commits': 0, 'mesh_queue_size': 0, 'beats': 0
        }
        self.start_time = time.time()
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update metrics."""
        for key in ['latency', 'throughput', 'pid_error']:
            if key in metrics:
                self.metrics_history[key].append(metrics[key])
                if len(self.metrics_history[key]) > 100:
                    self.metrics_history[key].pop(0)
        for key in ['ledger_commits', 'mesh_queue_size', 'beats']:
            if key in metrics:
                self.metrics_history[key] = metrics[key]
    
    def _create_metrics_table(self) -> Table:
        table = Table(title="VENOM Metrics", show_header=True)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Current", style="green", width=15)
        table.add_column("Average", style="yellow", width=15)
        
        latency_list = self.metrics_history['latency']
        current_lat = latency_list[-1] if latency_list else 0.0
        avg_lat = sum(latency_list) / len(latency_list) if latency_list else 0.0
        table.add_row("Latency (s)", f"{current_lat:.6f}", f"{avg_lat:.6f}")
        
        throughput_list = self.metrics_history['throughput']
        current_tp = throughput_list[-1] if throughput_list else 0.0
        avg_tp = sum(throughput_list) / len(throughput_list) if throughput_list else 0.0
        table.add_row("Throughput (b/s)", f"{current_tp:.2f}", f"{avg_tp:.2f}")
        
        pid_list = self.metrics_history['pid_error']
        current_pid = pid_list[-1] if pid_list else 0.0
        avg_pid = sum(pid_list) / len(pid_list) if pid_list else 0.0
        table.add_row("PID Error", f"{current_pid:.6f}", f"{avg_pid:.6f}")
        table.add_row("Ledger", str(self.metrics_history['ledger_commits']), "-")
        table.add_row("Mesh Queue", str(self.metrics_history['mesh_queue_size']), "-")
        return table
    
    def render(self) -> Layout:
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body"))
        layout["header"].update(Panel(Text("VENOM Dashboard", justify="center"), border_style="blue"))
        layout["body"].update(self._create_metrics_table())
        return layout
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get metrics snapshot for testing."""
        latency_list = self.metrics_history['latency']
        throughput_list = self.metrics_history['throughput']
        pid_list = self.metrics_history['pid_error']
        return {
            'latency_current': latency_list[-1] if latency_list else 0.0,
            'latency_avg': sum(latency_list) / len(latency_list) if latency_list else 0.0,
            'throughput_current': throughput_list[-1] if throughput_list else 0.0,
            'throughput_avg': sum(throughput_list) / len(throughput_list) if throughput_list else 0.0,
            'pid_error_current': pid_list[-1] if pid_list else 0.0,
            'pid_error_avg': sum(pid_list) / len(pid_list) if pid_list else 0.0,
            'ledger_commits': self.metrics_history['ledger_commits'],
            'mesh_queue_size': self.metrics_history['mesh_queue_size'],
            'beats': self.metrics_history['beats']
        }
