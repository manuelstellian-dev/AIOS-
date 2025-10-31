"""
Kubernetes Auto-Scaling System
Horizontal and Vertical Pod Autoscaling with custom metrics
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ScalingType(Enum):
    """Types of autoscaling"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class MetricType(Enum):
    """Metric types for scaling decisions"""
    CPU = "cpu"
    MEMORY = "memory"
    CUSTOM = "custom"

@dataclass
class HPAConfig:
    """Horizontal Pod Autoscaler configuration"""
    min_replicas: int
    max_replicas: int
    target_cpu_percent: float
    target_memory_percent: Optional[float] = None
    custom_metrics: Optional[Dict[str, float]] = None

@dataclass
class VPAConfig:
    """Vertical Pod Autoscaler configuration"""
    min_cpu: str  # e.g., "100m"
    max_cpu: str  # e.g., "2000m"
    min_memory: str  # e.g., "128Mi"
    max_memory: str  # e.g., "2Gi"
    mode: str = "Auto"  # Auto, Initial, Recreate, Off

@dataclass
class ScalingPolicy:
    """Scaling policy with thresholds and cooldowns"""
    metric_name: str
    metric_type: MetricType
    threshold: float
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_cooldown: int = 60  # seconds
    scale_down_cooldown: int = 300  # seconds

class K8sAutoscaler:
    """
    Kubernetes Autoscaler
    Manages HPA, VPA, and custom metrics-based scaling
    """
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.hpa_configs: Dict[str, HPAConfig] = {}
        self.vpa_configs: Dict[str, VPAConfig] = {}
        self.scaling_policies: Dict[str, List[ScalingPolicy]] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        logger.info(f"K8sAutoscaler initialized for namespace: {namespace}")
    
    def configure_hpa(self, deployment_name: str, config: HPAConfig) -> bool:
        """
        Configure Horizontal Pod Autoscaler for a deployment
        
        Args:
            deployment_name: Name of the deployment to scale
            config: HPA configuration
        
        Returns:
            True if configuration successful
        """
        if config.min_replicas > config.max_replicas:
            logger.error(f"Invalid HPA config: min_replicas > max_replicas")
            return False
        
        if config.target_cpu_percent <= 0 or config.target_cpu_percent > 100:
            logger.error(f"Invalid target_cpu_percent: {config.target_cpu_percent}")
            return False
        
        self.hpa_configs[deployment_name] = config
        logger.info(f"HPA configured for {deployment_name}: {config.min_replicas}-{config.max_replicas} replicas, target CPU: {config.target_cpu_percent}%")
        
        # Record in history
        self.scaling_history.append({
            "action": "configure_hpa",
            "deployment": deployment_name,
            "config": config
        })
        
        return True
    
    def configure_vpa(self, deployment_name: str, config: VPAConfig) -> bool:
        """
        Configure Vertical Pod Autoscaler for a deployment
        
        Args:
            deployment_name: Name of the deployment to scale
            config: VPA configuration
        
        Returns:
            True if configuration successful
        """
        valid_modes = ["Auto", "Initial", "Recreate", "Off"]
        if config.mode not in valid_modes:
            logger.error(f"Invalid VPA mode: {config.mode}")
            return False
        
        self.vpa_configs[deployment_name] = config
        logger.info(f"VPA configured for {deployment_name}: CPU {config.min_cpu}-{config.max_cpu}, Memory {config.min_memory}-{config.max_memory}, mode: {config.mode}")
        
        # Record in history
        self.scaling_history.append({
            "action": "configure_vpa",
            "deployment": deployment_name,
            "config": config
        })
        
        return True
    
    def scale_based_on_metrics(self, deployment_name: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Scale deployment based on current metrics
        
        Args:
            deployment_name: Name of the deployment
            metrics: Current metrics (cpu_percent, memory_percent, custom metrics)
        
        Returns:
            Scaling decision with action and target
        """
        if deployment_name not in self.hpa_configs:
            logger.warning(f"No HPA config for {deployment_name}")
            return {"action": "none", "reason": "no_hpa_config"}
        
        hpa_config = self.hpa_configs[deployment_name]
        current_replicas = metrics.get("current_replicas", hpa_config.min_replicas)
        cpu_percent = metrics.get("cpu_percent", 0)
        memory_percent = metrics.get("memory_percent", 0)
        
        # Determine scaling action based on CPU utilization
        decision = {"action": "none", "current_replicas": current_replicas}
        
        if cpu_percent > hpa_config.target_cpu_percent * 1.2:  # Scale up if 20% over target
            if current_replicas < hpa_config.max_replicas:
                target_replicas = min(current_replicas + 1, hpa_config.max_replicas)
                decision = {
                    "action": "scale_up",
                    "current_replicas": current_replicas,
                    "target_replicas": target_replicas,
                    "reason": f"CPU at {cpu_percent}% > target {hpa_config.target_cpu_percent}%"
                }
                logger.info(f"Scaling up {deployment_name}: {current_replicas} -> {target_replicas}")
        
        elif cpu_percent < hpa_config.target_cpu_percent * 0.5:  # Scale down if 50% below target
            if current_replicas > hpa_config.min_replicas:
                target_replicas = max(current_replicas - 1, hpa_config.min_replicas)
                decision = {
                    "action": "scale_down",
                    "current_replicas": current_replicas,
                    "target_replicas": target_replicas,
                    "reason": f"CPU at {cpu_percent}% < target {hpa_config.target_cpu_percent}%"
                }
                logger.info(f"Scaling down {deployment_name}: {current_replicas} -> {target_replicas}")
        
        # Record scaling decision
        self.scaling_history.append({
            "action": "scale_based_on_metrics",
            "deployment": deployment_name,
            "metrics": metrics,
            "decision": decision
        })
        
        return decision
    
    def get_scaling_status(self, deployment_name: str) -> Dict[str, Any]:
        """
        Get current scaling status for a deployment
        
        Args:
            deployment_name: Name of the deployment
        
        Returns:
            Status dict with HPA/VPA configs and history
        """
        status = {
            "deployment": deployment_name,
            "namespace": self.namespace,
            "hpa_configured": deployment_name in self.hpa_configs,
            "vpa_configured": deployment_name in self.vpa_configs
        }
        
        if deployment_name in self.hpa_configs:
            status["hpa_config"] = self.hpa_configs[deployment_name]
        
        if deployment_name in self.vpa_configs:
            status["vpa_config"] = self.vpa_configs[deployment_name]
        
        # Get recent history for this deployment
        status["recent_history"] = [
            h for h in self.scaling_history[-10:]
            if h.get("deployment") == deployment_name
        ]
        
        return status
    
    def apply_scaling_policy(self, deployment_name: str, policy: ScalingPolicy) -> bool:
        """
        Apply a custom scaling policy to a deployment
        
        Args:
            deployment_name: Name of the deployment
            policy: Scaling policy with thresholds and cooldowns
        
        Returns:
            True if policy applied successfully
        """
        if deployment_name not in self.scaling_policies:
            self.scaling_policies[deployment_name] = []
        
        # Validate policy
        if policy.scale_up_threshold <= policy.scale_down_threshold:
            logger.error(f"Invalid policy: scale_up_threshold must be > scale_down_threshold")
            return False
        
        self.scaling_policies[deployment_name].append(policy)
        logger.info(f"Applied scaling policy for {deployment_name}: {policy.metric_name} ({policy.metric_type.value})")
        
        # Record in history
        self.scaling_history.append({
            "action": "apply_scaling_policy",
            "deployment": deployment_name,
            "policy": policy
        })
        
        return True
    
    def get_all_scaling_configs(self) -> Dict[str, Any]:
        """
        Get all scaling configurations across all deployments
        
        Returns:
            Dict with HPA, VPA, and policy counts
        """
        return {
            "namespace": self.namespace,
            "total_hpa_configs": len(self.hpa_configs),
            "total_vpa_configs": len(self.vpa_configs),
            "total_policies": sum(len(policies) for policies in self.scaling_policies.values()),
            "deployments_with_hpa": list(self.hpa_configs.keys()),
            "deployments_with_vpa": list(self.vpa_configs.keys()),
            "history_count": len(self.scaling_history)
        }
