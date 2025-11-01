"""
Health Monitoring for VENOM Λ-GENESIS
System health monitoring with custom checks and background monitoring
"""
import time
import threading
import os
import psutil
from typing import Dict, Any, List, Callable, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    System health monitor with custom checks and built-in system checks
    Supports background monitoring and health status aggregation
    """
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize health monitor
        
        Args:
            check_interval: Interval in seconds between background checks
        """
        self.check_interval = check_interval
        self._checks: Dict[str, Dict[str, Any]] = {}
        self._check_history: Dict[str, deque] = {}
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def register_check(self, name: str, check_func: Callable, critical: bool = False) -> None:
        """
        Register a custom health check
        
        Args:
            name: Name of the health check
            check_func: Function that returns bool (True = healthy)
            critical: Whether this is a critical check
        """
        with self._lock:
            self._checks[name] = {
                "func": check_func,
                "critical": critical,
                "last_run": None,
                "last_status": None
            }
            if name not in self._check_history:
                self._check_history[name] = deque(maxlen=100)
    
    def unregister_check(self, name: str) -> bool:
        """
        Unregister a health check
        
        Args:
            name: Name of the check to remove
            
        Returns:
            True if check was removed, False if not found
        """
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                return True
            return False
    
    def run_checks(self) -> Dict[str, Dict]:
        """
        Run all registered health checks
        
        Returns:
            Dictionary with check results
        """
        results = {}
        
        with self._lock:
            for name, check_info in self._checks.items():
                try:
                    start_time = time.time()
                    status = check_info["func"]()
                    duration = time.time() - start_time
                    
                    result = {
                        "status": "pass" if status else "fail",
                        "critical": check_info["critical"],
                        "duration": duration,
                        "timestamp": time.time()
                    }
                    
                    # Update check info
                    check_info["last_run"] = time.time()
                    check_info["last_status"] = status
                    
                    # Add to history
                    self._check_history[name].append(result)
                    
                    results[name] = result
                    
                except Exception as e:
                    logger.error(f"Health check '{name}' failed with error: {e}")
                    result = {
                        "status": "error",
                        "critical": check_info["critical"],
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    results[name] = result
                    self._check_history[name].append(result)
        
        return results
    
    def get_health_status(self) -> str:
        """
        Get overall health status
        
        Returns:
            'healthy', 'degraded', or 'unhealthy'
        """
        check_results = self.run_checks()
        
        if not check_results:
            return "healthy"
        
        # Check for critical failures
        critical_failures = [
            name for name, result in check_results.items()
            if result.get("critical") and result.get("status") != "pass"
        ]
        
        if critical_failures:
            return "unhealthy"
        
        # Check for any failures
        failures = [
            name for name, result in check_results.items()
            if result.get("status") != "pass"
        ]
        
        if failures:
            return "degraded"
        
        return "healthy"
    
    def get_check_history(self, name: str, limit: int = 10) -> List[Dict]:
        """
        Get check history for a specific check
        
        Args:
            name: Name of the check
            limit: Maximum number of history entries to return
            
        Returns:
            List of check results
        """
        with self._lock:
            if name not in self._check_history:
                return []
            history = list(self._check_history[name])
            return history[-limit:]
    
    def check_cpu_usage(self, threshold: float = 80.0) -> bool:
        """
        Check CPU usage
        
        Args:
            threshold: CPU usage threshold percentage
            
        Returns:
            True if CPU usage is below threshold
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return cpu_percent < threshold
        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return False
    
    def check_memory_usage(self, threshold: float = 80.0) -> bool:
        """
        Check memory usage
        
        Args:
            threshold: Memory usage threshold percentage
            
        Returns:
            True if memory usage is below threshold
        """
        try:
            memory = psutil.virtual_memory()
            return memory.percent < threshold
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return False
    
    def check_disk_usage(self, threshold: float = 80.0, path: Optional[str] = None) -> bool:
        """
        Check disk usage
        
        Args:
            threshold: Disk usage threshold percentage
            path: Path to check (default: current working directory)
            
        Returns:
            True if disk usage is below threshold
        """
        try:
            check_path = path if path else os.getcwd()
            disk = psutil.disk_usage(check_path)
            return disk.percent < threshold
        except Exception as e:
            logger.error(f"Disk check failed: {e}")
            return False
    
    def check_process_alive(self, pid: int) -> bool:
        """
        Check if a process is alive
        
        Args:
            pid: Process ID to check
            
        Returns:
            True if process is running
        """
        try:
            return psutil.pid_exists(pid)
        except Exception as e:
            logger.error(f"Process check failed: {e}")
            return False
    
    def start_monitoring(self) -> None:
        """Start background monitoring thread"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info(f"Health monitoring started (interval: {self.check_interval}s)")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring thread"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                self.run_checks()
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.check_interval * 10):
                if not self._monitoring:
                    break
                time.sleep(0.1)
