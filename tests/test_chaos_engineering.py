"""Test Chaos Engineering"""
import pytest
from venom.testing.chaos_engineering import (
    ChaosEngine,
    ChaosType,
    TargetType,
    ChaosExperiment
)

def test_chaos_engine_init():
    """Test ChaosEngine initialization"""
    engine = ChaosEngine(namespace="venom-chaos")
    
    assert engine.namespace == "venom-chaos"
    assert len(engine.experiments) == 0
    assert len(engine.results) == 0

def test_inject_latency():
    """Test latency injection"""
    engine = ChaosEngine()
    
    target_selector = {"app": "venom", "tier": "api"}
    result = engine.inject_latency(
        target_selector=target_selector,
        latency_ms=150,
        duration=30,
        jitter_ms=20
    )
    
    assert result.success is True
    assert result.targets_affected > 0
    assert "latency" in result.experiment_name
    assert result.metrics["latency_injected_ms"] == 150
    assert result.metrics["jitter_ms"] == 20
    assert len(result.observations) > 0
    
    # Verify result was recorded
    assert len(engine.results) == 1

def test_inject_failure():
    """Test failure injection (pod kills)"""
    engine = ChaosEngine()
    
    target_selector = {"app": "venom"}
    
    # Test valid failure type
    result = engine.inject_failure(
        target_selector=target_selector,
        failure_type="pod_kill",
        count=3,
        interval=10
    )
    
    assert result.success is True
    assert result.targets_affected == 3
    assert "failure" in result.experiment_name
    assert result.metrics["targets_killed"] == 3
    assert result.metrics["failure_type"] == "pod_kill"
    
    # Test invalid failure type
    result_invalid = engine.inject_failure(
        target_selector=target_selector,
        failure_type="invalid_type",
        count=1,
        interval=10
    )
    
    assert result_invalid.success is False
    assert result_invalid.targets_affected == 0

def test_inject_resource_stress():
    """Test resource stress injection"""
    engine = ChaosEngine()
    
    target_selector = {"app": "venom", "component": "worker"}
    
    # Test CPU stress
    result = engine.inject_resource_stress(
        target_selector=target_selector,
        stress_type="cpu",
        intensity=0.8,
        duration=60
    )
    
    assert result.success is True
    assert result.targets_affected > 0
    assert "stress" in result.experiment_name
    assert result.metrics["stress_type"] == "cpu"
    assert result.metrics["intensity"] == 0.8
    assert result.metrics["duration_s"] == 60
    
    # Test invalid stress type
    result_invalid = engine.inject_resource_stress(
        target_selector=target_selector,
        stress_type="invalid",
        intensity=0.5,
        duration=30
    )
    assert result_invalid.success is False
    
    # Test invalid intensity
    result_invalid2 = engine.inject_resource_stress(
        target_selector=target_selector,
        stress_type="memory",
        intensity=1.5,  # > 1.0
        duration=30
    )
    assert result_invalid2.success is False

def test_run_chaos_scenario():
    """Test running a complete chaos scenario"""
    engine = ChaosEngine()
    
    scenario_experiments = [
        {
            "type": "latency",
            "target_selector": {"app": "venom"},
            "latency_ms": 100,
            "duration": 30,
            "jitter_ms": 10
        },
        {
            "type": "failure",
            "target_selector": {"app": "venom"},
            "failure_type": "pod_kill",
            "count": 2,
            "interval": 15
        },
        {
            "type": "stress",
            "target_selector": {"app": "venom"},
            "stress_type": "cpu",
            "intensity": 0.7,
            "duration": 30
        }
    ]
    
    scenario_result = engine.run_chaos_scenario(
        scenario_name="venom-resilience-test",
        experiments=scenario_experiments
    )
    
    assert scenario_result["scenario_name"] == "venom-resilience-test"
    assert scenario_result["total_experiments"] == 3
    assert scenario_result["successful_experiments"] == 3
    assert scenario_result["failed_experiments"] == 0
    assert len(scenario_result["experiments"]) == 3
    
    # Verify individual results were recorded
    assert len(engine.results) == 3

def test_generate_chaos_report():
    """Test generating chaos engineering report"""
    engine = ChaosEngine()
    
    # Run several experiments
    engine.inject_latency({"app": "venom"}, latency_ms=100, duration=30)
    engine.inject_failure({"app": "venom"}, failure_type="pod_kill", count=2)
    engine.inject_resource_stress({"app": "venom"}, stress_type="cpu", intensity=0.8, duration=30)
    
    report = engine.generate_chaos_report()
    
    assert report["total_experiments"] == 3
    assert report["successful_experiments"] == 3
    assert report["success_rate"] == 1.0
    assert "experiment_types" in report
    assert "recent_experiments" in report
    assert len(report["recent_experiments"]) == 3
    assert "insights" in report
    assert len(report["insights"]) > 0
    
    # Verify insights are generated
    assert any("resilience" in insight.lower() for insight in report["insights"])
