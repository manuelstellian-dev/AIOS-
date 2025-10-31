"""Test Kubernetes Auto-Scaling"""
import pytest
from venom.deployment.k8s_autoscale import (
    K8sAutoscaler,
    HPAConfig,
    VPAConfig,
    ScalingPolicy,
    MetricType
)

def test_k8s_autoscaler_init():
    """Test K8sAutoscaler initialization"""
    autoscaler = K8sAutoscaler(namespace="venom-prod")
    
    assert autoscaler.namespace == "venom-prod"
    assert len(autoscaler.hpa_configs) == 0
    assert len(autoscaler.vpa_configs) == 0
    assert len(autoscaler.scaling_history) == 0

def test_configure_hpa():
    """Test HPA configuration"""
    autoscaler = K8sAutoscaler()
    
    hpa_config = HPAConfig(
        min_replicas=2,
        max_replicas=10,
        target_cpu_percent=70.0,
        target_memory_percent=80.0
    )
    
    result = autoscaler.configure_hpa("venom-api", hpa_config)
    assert result is True
    assert "venom-api" in autoscaler.hpa_configs
    assert autoscaler.hpa_configs["venom-api"].min_replicas == 2
    assert autoscaler.hpa_configs["venom-api"].max_replicas == 10
    
    # Test invalid configuration
    invalid_config = HPAConfig(
        min_replicas=10,
        max_replicas=2,  # max < min
        target_cpu_percent=70.0
    )
    result = autoscaler.configure_hpa("venom-api-invalid", invalid_config)
    assert result is False

def test_configure_vpa():
    """Test VPA configuration"""
    autoscaler = K8sAutoscaler()
    
    vpa_config = VPAConfig(
        min_cpu="100m",
        max_cpu="2000m",
        min_memory="128Mi",
        max_memory="2Gi",
        mode="Auto"
    )
    
    result = autoscaler.configure_vpa("venom-worker", vpa_config)
    assert result is True
    assert "venom-worker" in autoscaler.vpa_configs
    assert autoscaler.vpa_configs["venom-worker"].min_cpu == "100m"
    assert autoscaler.vpa_configs["venom-worker"].mode == "Auto"
    
    # Test invalid mode
    invalid_config = VPAConfig(
        min_cpu="100m",
        max_cpu="2000m",
        min_memory="128Mi",
        max_memory="2Gi",
        mode="InvalidMode"
    )
    result = autoscaler.configure_vpa("venom-worker-invalid", invalid_config)
    assert result is False

def test_scale_based_on_metrics():
    """Test scaling decisions based on metrics"""
    autoscaler = K8sAutoscaler()
    
    # Configure HPA first
    hpa_config = HPAConfig(
        min_replicas=2,
        max_replicas=10,
        target_cpu_percent=70.0
    )
    autoscaler.configure_hpa("venom-api", hpa_config)
    
    # Test scale up scenario (CPU > target * 1.2)
    metrics = {
        "current_replicas": 3,
        "cpu_percent": 90.0,  # Above 70 * 1.2 = 84
        "memory_percent": 60.0
    }
    decision = autoscaler.scale_based_on_metrics("venom-api", metrics)
    assert decision["action"] == "scale_up"
    assert decision["target_replicas"] == 4
    
    # Test scale down scenario (CPU < target * 0.5)
    metrics = {
        "current_replicas": 5,
        "cpu_percent": 30.0,  # Below 70 * 0.5 = 35
        "memory_percent": 40.0
    }
    decision = autoscaler.scale_based_on_metrics("venom-api", metrics)
    assert decision["action"] == "scale_down"
    assert decision["target_replicas"] == 4
    
    # Test no scaling scenario
    metrics = {
        "current_replicas": 3,
        "cpu_percent": 65.0,  # Within acceptable range
        "memory_percent": 50.0
    }
    decision = autoscaler.scale_based_on_metrics("venom-api", metrics)
    assert decision["action"] == "none"

def test_get_scaling_status():
    """Test getting scaling status"""
    autoscaler = K8sAutoscaler()
    
    # Configure both HPA and VPA
    hpa_config = HPAConfig(min_replicas=2, max_replicas=10, target_cpu_percent=70.0)
    vpa_config = VPAConfig(min_cpu="100m", max_cpu="2000m", min_memory="128Mi", max_memory="2Gi")
    
    autoscaler.configure_hpa("venom-api", hpa_config)
    autoscaler.configure_vpa("venom-api", vpa_config)
    
    status = autoscaler.get_scaling_status("venom-api")
    
    assert status["deployment"] == "venom-api"
    assert status["hpa_configured"] is True
    assert status["vpa_configured"] is True
    assert "hpa_config" in status
    assert "vpa_config" in status
    assert "recent_history" in status

def test_apply_scaling_policy():
    """Test applying custom scaling policies"""
    autoscaler = K8sAutoscaler()
    
    policy = ScalingPolicy(
        metric_name="custom_queue_depth",
        metric_type=MetricType.CUSTOM,
        threshold=100.0,
        scale_up_threshold=150.0,
        scale_down_threshold=50.0,
        scale_up_cooldown=60,
        scale_down_cooldown=300
    )
    
    result = autoscaler.apply_scaling_policy("venom-worker", policy)
    assert result is True
    assert "venom-worker" in autoscaler.scaling_policies
    assert len(autoscaler.scaling_policies["venom-worker"]) == 1
    
    # Test invalid policy (scale_up <= scale_down)
    invalid_policy = ScalingPolicy(
        metric_name="invalid_metric",
        metric_type=MetricType.CPU,
        threshold=100.0,
        scale_up_threshold=50.0,  # Invalid: should be > scale_down
        scale_down_threshold=100.0,
        scale_up_cooldown=60,
        scale_down_cooldown=300
    )
    
    result = autoscaler.apply_scaling_policy("venom-worker", invalid_policy)
    assert result is False
    
    # Verify overall configs
    all_configs = autoscaler.get_all_scaling_configs()
    assert all_configs["total_policies"] == 1
