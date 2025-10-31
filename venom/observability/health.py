"""
Health Checker for VENOM Λ-GENESIS
Monitors system health and provides readiness/liveness probes
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """
    System health checker with readiness and liveness probes
    Monitors component health and system stability
    """
    
    def __init__(self, arbiter=None):
        """
        Initialize health checker
        
        Args:
            arbiter: Optional Arbiter instance to monitor
        """
        self.arbiter = arbiter
        self.start_time = time.time()
        self.last_beat_time: Optional[float] = None
        self.health_history: List[Dict[str, Any]] = []
        
    def check_readiness(self) -> Dict[str, Any]:
        """
        Check if system is ready to serve requests
        
        Returns:
            Readiness status dictionary
        """
        checks = {}
        ready = True
        
        # Check if components are initialized
        if self.arbiter:
            checks["arbiter"] = "ready"
            checks["pulse"] = "ready" if self.arbiter.pulse else "not_ready"
            checks["pid"] = "ready" if self.arbiter.pid else "not_ready"
            checks["ledger"] = "ready" if self.arbiter.ledger else "not_ready"
            
            # Check if system is running
            checks["running"] = "yes" if self.arbiter.running else "no"
            
            # Not ready if any component missing
            if not all(v == "ready" or v == "yes" for v in checks.values()):
                ready = False
        else:
            checks["arbiter"] = "not_initialized"
            ready = False
        
        return {
            "status": "ready" if ready else "not_ready",
            "checks": checks,
            "timestamp": time.time()
        }
    
    def check_liveness(self) -> Dict[str, Any]:
        """
        Check if system is alive and functioning
        
        Returns:
            Liveness status dictionary
        """
        alive = True
        checks = {}
        
        # Check uptime
        uptime = time.time() - self.start_time
        checks["uptime_seconds"] = uptime
        
        # Check if beats are progressing
        if self.last_beat_time:
            time_since_last_beat = time.time() - self.last_beat_time
            checks["time_since_last_beat_seconds"] = time_since_last_beat
            
            # If no beat in last 60 seconds, consider unhealthy
            if time_since_last_beat > 60:
                checks["beat_status"] = "stalled"
                alive = False
            else:
                checks["beat_status"] = "progressing"
        else:
            checks["beat_status"] = "not_started"
        
        # Check PID stability if arbiter available
        if self.arbiter and hasattr(self.arbiter, 'pid'):
            try:
                is_stable = self.arbiter.pid.is_stable(window=5)
                checks["pid_stable"] = is_stable
            except:
                checks["pid_stable"] = "unknown"
        
        return {
            "status": "alive" if alive else "dead",
            "checks": checks,
            "timestamp": time.time()
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        
        Returns:
            Full health status
        """
        readiness = self.check_readiness()
        liveness = self.check_liveness()
        
        # Determine overall health
        if readiness["status"] == "ready" and liveness["status"] == "alive":
            status = HealthStatus.HEALTHY
        elif readiness["status"] == "not_ready" or liveness["status"] == "dead":
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.DEGRADED
        
        health_report = {
            "status": status.value,
            "readiness": readiness,
            "liveness": liveness,
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": time.time()
        }
        
        # Add to history
        self.health_history.append(health_report)
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        return health_report
    
    def record_beat(self):
        """Record a beat execution"""
        self.last_beat_time = time.time()
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        return self.health_history[-limit:]
    
    def is_healthy(self) -> bool:
        """Check if system is currently healthy"""
        health = self.check_health()
        return health["status"] == HealthStatus.HEALTHY.value
