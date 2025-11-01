"""
Theta Monitor - Real-time system health monitoring for VENOM Ω-AIOS

Continuously monitors:
- CPU health (H_CPU)
- Memory health (H_MEM)
- Thermal health (H_TERM)
- System theta (θ)

Exports Prometheus metrics for observability.
"""

import logging
import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThetaSnapshot:
    """Snapshot of system theta metrics"""
    timestamp: float
    theta: float
    cpu_health: float
    memory_health: float
    thermal_health: float
    compression_factor: float
    mode: str


class ThetaMonitor:
    """
    Real-time system health monitor
    
    Tracks theta (θ) and component health metrics:
    - H_CPU: CPU health [0-1]
    - H_MEM: Memory health [0-1]
    - H_TERM: Thermal health [0-1]
    - θ = 0.3×H_CPU + 0.3×H_MEM + 0.4×H_TERM
    
    Provides Prometheus metrics for observability.
    """
    
    def __init__(
        self,
        scanner=None,
        interval: float = 1.0
    ):
        """
        Initialize Theta Monitor
        
        Args:
            scanner: UniversalHardwareScanner instance (optional)
            interval: Monitoring interval in seconds
        """
        self.scanner = scanner
        self.interval = interval
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Current metrics
        self.current_theta: float = 0.0
        self.cpu_health: float = 0.0
        self.memory_health: float = 0.0
        self.thermal_health: float = 0.0
        self.compression_factor: float = 0.0
        
        # History (keep last 100 snapshots)
        self.history: list = []
        self.max_history = 100
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Initialize scanner if not provided
        if self.scanner is None:
            try:
                from ..hardware.universal_scanner import UniversalHardwareScanner
                self.scanner = UniversalHardwareScanner()
                logger.info("📊 ThetaMonitor: Initialized with auto-detected hardware")
            except Exception as e:
                logger.warning(f"Could not initialize hardware scanner: {e}")
        
        # Initialize Möbius engine for compression calculation
        try:
            from ..sync.adaptive_mobius_engine import AdaptiveMobiusEngine
            self.mobius_engine = AdaptiveMobiusEngine(auto_detect=False)
        except Exception as e:
            logger.warning(f"Could not initialize Möbius engine: {e}")
            self.mobius_engine = None
    
    def get_cpu_health(self) -> float:
        """
        Get CPU health score [0-1]
        
        Based on CPU usage:
        - 0% usage = 1.0 health
        - 100% usage = 0.0 health
        
        Returns:
            CPU health score
        """
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            health = 1.0 - (cpu_percent / 100.0)
            return max(0.0, min(1.0, health))
        except Exception as e:
            logger.warning(f"Error getting CPU health: {e}")
            return 0.5  # Default
    
    def get_memory_health(self) -> float:
        """
        Get memory health score [0-1]
        
        Based on memory usage:
        - 0% usage = 1.0 health
        - 100% usage = 0.0 health
        
        Returns:
            Memory health score
        """
        try:
            import psutil
            mem = psutil.virtual_memory()
            health = 1.0 - (mem.percent / 100.0)
            return max(0.0, min(1.0, health))
        except Exception as e:
            logger.warning(f"Error getting memory health: {e}")
            return 0.5  # Default
    
    def get_thermal_health(self) -> float:
        """
        Get thermal health score [0-1]
        
        Based on CPU temperature:
        - < 50°C: 1.0
        - 50-70°C: linear decrease to 0.5
        - 70-90°C: linear decrease to 0.0
        - > 90°C: 0.0
        
        Returns:
            Thermal health score
        """
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return 0.8  # Default if no sensors
            
            # Find CPU temperature
            cpu_temp = None
            for name, entries in temps.items():
                if 'coretemp' in name.lower() or 'cpu' in name.lower():
                    if entries:
                        cpu_temp = sum(e.current for e in entries) / len(entries)
                        break
            
            if cpu_temp is None:
                # Use first available temperature
                for name, entries in temps.items():
                    if entries:
                        cpu_temp = sum(e.current for e in entries) / len(entries)
                        break
            
            if cpu_temp is None:
                return 0.8  # Default
            
            # Map temperature to health
            if cpu_temp < 50:
                return 1.0
            elif cpu_temp < 70:
                return 1.0 - ((cpu_temp - 50) / 40.0)
            elif cpu_temp < 90:
                return 0.5 - ((cpu_temp - 70) / 40.0)
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Error getting thermal health: {e}")
            return 0.8  # Default
    
    def calculate_theta(self) -> float:
        """
        Calculate system theta (θ)
        
        Formula: θ = 0.3×H_CPU + 0.3×H_MEM + 0.4×H_TERM
        
        Returns:
            Theta value [0-1]
        """
        theta = (
            0.3 * self.cpu_health +
            0.3 * self.memory_health +
            0.4 * self.thermal_health
        )
        return max(0.0, min(1.0, theta))
    
    def _update_metrics(self):
        """Update current metrics (internal)"""
        with self.lock:
            self.cpu_health = self.get_cpu_health()
            self.memory_health = self.get_memory_health()
            self.thermal_health = self.get_thermal_health()
            self.current_theta = self.calculate_theta()
            
            # Calculate compression factor if Möbius engine available
            if self.mobius_engine:
                self.compression_factor = self.mobius_engine.theta_compression(
                    self.current_theta
                )
            else:
                self.compression_factor = 0.0
            
            # Get mode
            if self.mobius_engine:
                mode = self.mobius_engine.get_mode_name(self.current_theta)
            else:
                mode = "UNKNOWN"
            
            # Add to history
            snapshot = ThetaSnapshot(
                timestamp=time.time(),
                theta=self.current_theta,
                cpu_health=self.cpu_health,
                memory_health=self.memory_health,
                thermal_health=self.thermal_health,
                compression_factor=self.compression_factor,
                mode=mode
            )
            
            self.history.append(snapshot)
            
            # Trim history
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
    
    def _monitor_loop(self):
        """Monitoring loop (runs in thread)"""
        logger.info(f"📊 ThetaMonitor: Started monitoring (interval: {self.interval}s)")
        
        while self.running:
            try:
                self._update_metrics()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)
        
        logger.info("📊 ThetaMonitor: Stopped monitoring")
    
    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.running:
            logger.warning("ThetaMonitor already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ThetaMonitor"
        )
        self.monitor_thread.start()
        
        # Initial update
        self._update_metrics()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.running:
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
    
    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get current theta metrics
        
        Returns:
            Dictionary with current metrics
        """
        with self.lock:
            return {
                'theta': self.current_theta,
                'cpu_health': self.cpu_health,
                'memory_health': self.memory_health,
                'thermal_health': self.thermal_health,
                'compression_factor': self.compression_factor
            }
    
    def get_history(self, n: Optional[int] = None) -> list:
        """
        Get historical snapshots
        
        Args:
            n: Number of recent snapshots (None for all)
            
        Returns:
            List of ThetaSnapshot objects
        """
        with self.lock:
            if n is None:
                return list(self.history)
            else:
                return list(self.history[-n:])
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format
        
        Metrics:
        - venom_theta_current
        - venom_theta_cpu_health
        - venom_theta_memory_health
        - venom_theta_thermal_health
        - venom_theta_compression_factor
        
        Returns:
            Prometheus-formatted metrics string
        """
        metrics = self.get_current_metrics()
        
        lines = [
            "# HELP venom_theta_current Current system theta (θ) value",
            "# TYPE venom_theta_current gauge",
            f"venom_theta_current {metrics['theta']:.6f}",
            "",
            "# HELP venom_theta_cpu_health CPU health score [0-1]",
            "# TYPE venom_theta_cpu_health gauge",
            f"venom_theta_cpu_health {metrics['cpu_health']:.6f}",
            "",
            "# HELP venom_theta_memory_health Memory health score [0-1]",
            "# TYPE venom_theta_memory_health gauge",
            f"venom_theta_memory_health {metrics['memory_health']:.6f}",
            "",
            "# HELP venom_theta_thermal_health Thermal health score [0-1]",
            "# TYPE venom_theta_thermal_health gauge",
            f"venom_theta_thermal_health {metrics['thermal_health']:.6f}",
            "",
            "# HELP venom_theta_compression_factor Theta compression factor Θ(θ)",
            "# TYPE venom_theta_compression_factor gauge",
            f"venom_theta_compression_factor {metrics['compression_factor']:.6f}",
            ""
        ]
        
        return "\n".join(lines)
    
    def print_status(self):
        """Print current status"""
        metrics = self.get_current_metrics()
        
        mode = "UNKNOWN"
        if self.mobius_engine:
            mode = self.mobius_engine.get_mode_name(metrics['theta'])
        
        print("\n" + "="*60)
        print("📊 VENOM Ω-AIOS Theta Monitor Status")
        print("="*60)
        
        print(f"\n🎯 System Theta:")
        print(f"  θ (theta):           {metrics['theta']:.3f} [{mode}]")
        print(f"  Θ(θ) (compression):  {metrics['compression_factor']:.3f}")
        
        print(f"\n💚 Component Health:")
        print(f"  CPU Health:          {metrics['cpu_health']:.3f} {'✅' if metrics['cpu_health'] > 0.7 else '⚠️' if metrics['cpu_health'] > 0.5 else '❌'}")
        print(f"  Memory Health:       {metrics['memory_health']:.3f} {'✅' if metrics['memory_health'] > 0.7 else '⚠️' if metrics['memory_health'] > 0.5 else '❌'}")
        print(f"  Thermal Health:      {metrics['thermal_health']:.3f} {'✅' if metrics['thermal_health'] > 0.7 else '⚠️' if metrics['thermal_health'] > 0.5 else '❌'}")
        
        print(f"\n📈 History:")
        print(f"  Snapshots:           {len(self.history)}")
        
        if len(self.history) >= 2:
            # Show trend
            recent = self.history[-10:] if len(self.history) >= 10 else self.history
            theta_trend = recent[-1].theta - recent[0].theta
            trend_symbol = "📈" if theta_trend > 0.01 else "📉" if theta_trend < -0.01 else "➡️"
            print(f"  Theta Trend:         {trend_symbol} ({theta_trend:+.3f})")
        
        print("="*60 + "\n")


def demo_monitor():
    """Demo of theta monitoring"""
    print("📊 VENOM Ω-AIOS Theta Monitor Demo\n")
    
    monitor = ThetaMonitor(interval=0.5)
    monitor.start_monitoring()
    
    try:
        # Monitor for 10 seconds
        for i in range(10):
            time.sleep(1)
            if i % 2 == 0:
                monitor.print_status()
        
    finally:
        monitor.stop_monitoring()
    
    print("\n✅ Monitoring complete")


if __name__ == "__main__":
    demo_monitor()
