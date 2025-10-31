"""
Chaos Engineering System
Inject failures, latency, and resource stress to test resilience
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChaosType(Enum):
    """Types of chaos experiments"""
    LATENCY = "latency"
    FAILURE = "failure"
    RESOURCE_STRESS = "resource_stress"
    NETWORK_PARTITION = "network_partition"

class TargetType(Enum):
    """Target types for chaos injection"""
    POD = "pod"
    NODE = "node"
    NETWORK = "network"
    STORAGE = "storage"

@dataclass
class ChaosExperiment:
    """Chaos experiment configuration"""
    name: str
    chaos_type: ChaosType
    target_type: TargetType
    target_selector: Dict[str, str]  # e.g., {"app": "venom"}
    duration: int  # seconds
    parameters: Dict[str, Any]
    
@dataclass
class ChaosResult:
    """Result of a chaos experiment"""
    experiment_name: str
    success: bool
    start_time: float
    end_time: float
    targets_affected: int
    observations: List[str]
    metrics: Dict[str, float]

class ChaosEngine:
    """
    Chaos Engineering Engine
    Injects controlled chaos to test system resilience
    """
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.results: List[ChaosResult] = []
        self.active_experiments: Dict[str, float] = {}  # experiment_name -> start_time
        logger.info(f"ChaosEngine initialized for namespace: {namespace}")
    
    def inject_latency(self, 
                       target_selector: Dict[str, str],
                       latency_ms: int = 100,
                       duration: int = 60,
                       jitter_ms: int = 10) -> ChaosResult:
        """
        Inject network latency into target pods
        
        Args:
            target_selector: Labels to select target pods
            latency_ms: Base latency to inject in milliseconds
            duration: Duration of the experiment in seconds
            jitter_ms: Random jitter to add to latency
        
        Returns:
            ChaosResult with experiment outcome
        """
        experiment_name = f"latency-{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Injecting {latency_ms}ms latency (+/- {jitter_ms}ms) for {duration}s")
        
        # Simulate latency injection
        observations = [
            f"Selected targets: {target_selector}",
            f"Injecting {latency_ms}ms base latency with {jitter_ms}ms jitter",
            f"Duration: {duration}s"
        ]
        
        # Simulate experiment execution
        targets_affected = len(target_selector)
        
        # Collect metrics during experiment
        metrics = {
            "latency_injected_ms": latency_ms,
            "jitter_ms": jitter_ms,
            "duration_s": duration,
            "targets_affected": targets_affected,
            "success_rate": 0.95  # Simulated
        }
        
        end_time = time.time()
        
        result = ChaosResult(
            experiment_name=experiment_name,
            success=True,
            start_time=start_time,
            end_time=end_time,
            targets_affected=targets_affected,
            observations=observations,
            metrics=metrics
        )
        
        self.results.append(result)
        logger.info(f"Latency injection completed: {experiment_name}")
        
        return result
    
    def inject_failure(self,
                       target_selector: Dict[str, str],
                       failure_type: str = "pod_kill",
                       count: int = 1,
                       interval: int = 30) -> ChaosResult:
        """
        Inject failures (pod kills, node failures, etc.)
        
        Args:
            target_selector: Labels to select target pods
            failure_type: Type of failure (pod_kill, pod_failure, node_failure)
            count: Number of targets to fail
            interval: Interval between failures in seconds
        
        Returns:
            ChaosResult with experiment outcome
        """
        experiment_name = f"failure-{failure_type}-{int(time.time())}"
        start_time = time.time()
        
        valid_failure_types = ["pod_kill", "pod_failure", "node_failure", "container_kill"]
        if failure_type not in valid_failure_types:
            logger.error(f"Invalid failure type: {failure_type}")
            return ChaosResult(
                experiment_name=experiment_name,
                success=False,
                start_time=start_time,
                end_time=time.time(),
                targets_affected=0,
                observations=[f"Invalid failure type: {failure_type}"],
                metrics={}
            )
        
        logger.info(f"Injecting {failure_type} failure: {count} targets, {interval}s interval")
        
        observations = [
            f"Failure type: {failure_type}",
            f"Target selector: {target_selector}",
            f"Count: {count}",
            f"Interval: {interval}s"
        ]
        
        # Simulate failure injection
        for i in range(count):
            observations.append(f"Killed target {i+1}/{count}")
            if i < count - 1:
                time.sleep(0.1)  # Small delay for simulation
        
        metrics = {
            "failure_type": failure_type,
            "targets_killed": count,
            "interval_s": interval,
            "recovery_time_s": count * interval * 0.5  # Simulated recovery time
        }
        
        end_time = time.time()
        
        result = ChaosResult(
            experiment_name=experiment_name,
            success=True,
            start_time=start_time,
            end_time=end_time,
            targets_affected=count,
            observations=observations,
            metrics=metrics
        )
        
        self.results.append(result)
        logger.info(f"Failure injection completed: {experiment_name}")
        
        return result
    
    def inject_resource_stress(self,
                                target_selector: Dict[str, str],
                                stress_type: str = "cpu",
                                intensity: float = 0.8,
                                duration: int = 60) -> ChaosResult:
        """
        Inject resource stress (CPU, memory, disk I/O)
        
        Args:
            target_selector: Labels to select target pods
            stress_type: Type of stress (cpu, memory, io)
            intensity: Stress intensity (0.0 to 1.0)
            duration: Duration of stress in seconds
        
        Returns:
            ChaosResult with experiment outcome
        """
        experiment_name = f"stress-{stress_type}-{int(time.time())}"
        start_time = time.time()
        
        valid_stress_types = ["cpu", "memory", "io", "disk"]
        if stress_type not in valid_stress_types:
            logger.error(f"Invalid stress type: {stress_type}")
            return ChaosResult(
                experiment_name=experiment_name,
                success=False,
                start_time=start_time,
                end_time=time.time(),
                targets_affected=0,
                observations=[f"Invalid stress type: {stress_type}"],
                metrics={}
            )
        
        if intensity < 0.0 or intensity > 1.0:
            logger.error(f"Invalid intensity: {intensity} (must be 0.0-1.0)")
            return ChaosResult(
                experiment_name=experiment_name,
                success=False,
                start_time=start_time,
                end_time=time.time(),
                targets_affected=0,
                observations=[f"Invalid intensity: {intensity}"],
                metrics={}
            )
        
        logger.info(f"Injecting {stress_type} stress at {intensity*100}% for {duration}s")
        
        observations = [
            f"Stress type: {stress_type}",
            f"Target selector: {target_selector}",
            f"Intensity: {intensity*100}%",
            f"Duration: {duration}s"
        ]
        
        targets_affected = len(target_selector)
        
        # Simulate stress injection
        observations.append(f"Stress applied to {targets_affected} targets")
        
        metrics = {
            "stress_type": stress_type,
            "intensity": intensity,
            "duration_s": duration,
            "targets_affected": targets_affected,
            "avg_response_time_ms": 50 * (1 + intensity),  # Simulated impact
            "error_rate": intensity * 0.01  # Simulated error rate
        }
        
        end_time = time.time()
        
        result = ChaosResult(
            experiment_name=experiment_name,
            success=True,
            start_time=start_time,
            end_time=end_time,
            targets_affected=targets_affected,
            observations=observations,
            metrics=metrics
        )
        
        self.results.append(result)
        logger.info(f"Resource stress completed: {experiment_name}")
        
        return result
    
    def run_chaos_scenario(self, scenario_name: str, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a predefined chaos scenario with multiple experiments
        
        Args:
            scenario_name: Name of the scenario
            experiments: List of experiment configurations
        
        Returns:
            Scenario results with all experiment outcomes
        """
        logger.info(f"Running chaos scenario: {scenario_name}")
        start_time = time.time()
        
        scenario_results = {
            "scenario_name": scenario_name,
            "start_time": start_time,
            "experiments": [],
            "total_experiments": len(experiments),
            "successful_experiments": 0,
            "failed_experiments": 0
        }
        
        for exp_config in experiments:
            exp_type = exp_config.get("type")
            
            if exp_type == "latency":
                result = self.inject_latency(
                    target_selector=exp_config.get("target_selector", {}),
                    latency_ms=exp_config.get("latency_ms", 100),
                    duration=exp_config.get("duration", 60),
                    jitter_ms=exp_config.get("jitter_ms", 10)
                )
            elif exp_type == "failure":
                result = self.inject_failure(
                    target_selector=exp_config.get("target_selector", {}),
                    failure_type=exp_config.get("failure_type", "pod_kill"),
                    count=exp_config.get("count", 1),
                    interval=exp_config.get("interval", 30)
                )
            elif exp_type == "stress":
                result = self.inject_resource_stress(
                    target_selector=exp_config.get("target_selector", {}),
                    stress_type=exp_config.get("stress_type", "cpu"),
                    intensity=exp_config.get("intensity", 0.8),
                    duration=exp_config.get("duration", 60)
                )
            else:
                logger.warning(f"Unknown experiment type: {exp_type}")
                continue
            
            scenario_results["experiments"].append({
                "name": result.experiment_name,
                "success": result.success,
                "targets_affected": result.targets_affected
            })
            
            if result.success:
                scenario_results["successful_experiments"] += 1
            else:
                scenario_results["failed_experiments"] += 1
        
        scenario_results["end_time"] = time.time()
        scenario_results["total_duration_s"] = scenario_results["end_time"] - start_time
        
        logger.info(f"Chaos scenario completed: {scenario_name} ({scenario_results['successful_experiments']}/{scenario_results['total_experiments']} successful)")
        
        return scenario_results
    
    def generate_chaos_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive chaos engineering report
        
        Returns:
            Report with all experiments, success rates, and insights
        """
        if not self.results:
            return {
                "total_experiments": 0,
                "message": "No chaos experiments run yet"
            }
        
        total_experiments = len(self.results)
        successful_experiments = sum(1 for r in self.results if r.success)
        failed_experiments = total_experiments - successful_experiments
        
        # Aggregate metrics
        total_targets_affected = sum(r.targets_affected for r in self.results)
        
        # Get experiment type breakdown
        experiment_types = {}
        for result in self.results:
            exp_type = result.experiment_name.split('-')[0]
            experiment_types[exp_type] = experiment_types.get(exp_type, 0) + 1
        
        # Calculate average metrics
        avg_duration = sum(r.end_time - r.start_time for r in self.results) / total_experiments
        
        report = {
            "total_experiments": total_experiments,
            "successful_experiments": successful_experiments,
            "failed_experiments": failed_experiments,
            "success_rate": successful_experiments / total_experiments if total_experiments > 0 else 0,
            "total_targets_affected": total_targets_affected,
            "experiment_types": experiment_types,
            "avg_experiment_duration_s": avg_duration,
            "recent_experiments": [
                {
                    "name": r.experiment_name,
                    "success": r.success,
                    "targets_affected": r.targets_affected,
                    "duration_s": r.end_time - r.start_time
                }
                for r in self.results[-5:]  # Last 5 experiments
            ],
            "insights": self._generate_insights()
        }
        
        return report
    
    def _generate_insights(self) -> List[str]:
        """Generate insights from chaos experiments"""
        insights = []
        
        if not self.results:
            return ["No experiments to analyze"]
        
        successful_count = sum(1 for r in self.results if r.success)
        total_count = len(self.results)
        success_rate = successful_count / total_count
        
        if success_rate >= 0.95:
            insights.append("System shows excellent resilience (>95% success rate)")
        elif success_rate >= 0.80:
            insights.append("System shows good resilience (>80% success rate)")
        else:
            insights.append("System resilience needs improvement (<80% success rate)")
        
        # Check for specific patterns
        failure_experiments = [r for r in self.results if "failure" in r.experiment_name]
        if failure_experiments:
            failure_success_rate = sum(1 for r in failure_experiments if r.success) / len(failure_experiments)
            if failure_success_rate < 1.0:
                insights.append(f"Some failure injection experiments encountered issues")
        
        stress_experiments = [r for r in self.results if "stress" in r.experiment_name]
        if stress_experiments:
            insights.append(f"Conducted {len(stress_experiments)} resource stress tests")
        
        return insights
