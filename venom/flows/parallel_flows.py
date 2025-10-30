"""
Parallel flows implementation: R, B, E, O as Cores
Each core represents a different dimension of the fractal organism
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


class BaseCore(ABC):
    """Base class for all parallel cores"""
    
    def __init__(self, name: str):
        self.name = name
        self.state: Dict[str, Any] = {}
        self.iteration = 0
        
    @abstractmethod
    def compute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute core logic synchronized with T_Λ pulse"""
        pass
    
    def execute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Execute core with logging and state management"""
        self.iteration += 1
        logger.debug(f"{self.name} core executing iteration {self.iteration}")
        
        result = self.compute(genome, features)
        self.state.update(result)
        
        return {
            "core": self.name,
            "iteration": self.iteration,
            "timestamp": time.time(),
            **result
        }


class RegenCore(BaseCore):
    """R Core - Regeneration/Repair dimension (repair+replicate)"""
    
    def __init__(self):
        super().__init__("R")
    
    def compute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute repair and replication urgency"""
        # Extract risk and anomalies
        risk = genome.get("risk", {})
        anoms = risk.get("anoms", 0)
        
        # Calculate urgency based on anomalies (higher anoms = higher urgency)
        urgency = min(0.9, anoms / 100.0) if anoms > 0 else 0.4
        
        # Cost increases with urgency
        cost = urgency * 0.5
        
        return {
            "urgency": urgency,
            "cost": cost,
            "action": "repair+replicate"
        }


class BalanceCore(BaseCore):
    """B Core - Balance/Stabilization dimension"""
    
    def __init__(self):
        super().__init__("B")
        self.balance_state = 0.5
    
    def compute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute balance and provide PID parameters"""
        # Extract stability metrics
        t_lambda = features.get("t_lambda", 0.02)
        
        # Calculate conservation score (tendency to maintain stability)
        conserve = 0.3 + (1.0 - abs(t_lambda - 0.02)) * 0.2
        conserve = max(0.0, min(1.0, conserve))
        
        # Update balance state
        self.balance_state = (self.balance_state + conserve) / 2.0
        
        # Provide PID parameters
        return {
            "conserve": conserve,
            "kp": 0.6,
            "ki": 0.1,
            "kd": 0.05,
            "balance_state": self.balance_state
        }


class EntropyCore(BaseCore):
    """E Core - Entropy/Risk Scanning dimension"""
    
    def __init__(self, entropy_model=None):
        super().__init__("E")
        self.entropy_model = entropy_model
    
    def compute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute threat score using EntropyModel"""
        # Extract anomalies from genome
        risk = genome.get("risk", {})
        total_anoms = risk.get("anoms", 0)
        
        # Add anomalies from features if present
        if "anoms" in features:
            total_anoms += features["anoms"]
        
        # Infer threat score using entropy model
        if self.entropy_model:
            threat_score = self.entropy_model.infer_threat(total_anoms)
        else:
            # Fallback: simple sigmoid-like approximation
            import math
            threat_score = 1.0 / (1.0 + math.exp(-total_anoms / 10.0))
        
        explanation = f"Threat inferred from {total_anoms} anomalies"
        version = "0.1.0"
        
        return {
            "threat_score": threat_score,
            "explanation": explanation,
            "version": version
        }


class OptimizeCore(BaseCore):
    """O Core - Optimization/Reinvestment dimension"""
    
    def __init__(self):
        super().__init__("O")
    
    def compute(self, genome: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute expected gain for optimization"""
        # Extract optimization weight from genome
        weights = genome.get("weights", {})
        o_weight = weights.get("O", 1.0)
        
        # Calculate expected gain (higher weight = higher potential gain)
        expected_gain = min(0.5, o_weight * 0.12)
        
        return {
            "expected_gain": expected_gain,
            "action": "reinvest+transform"
        }


# Aliases for backward compatibility
RFlow = RegenCore
BFlow = BalanceCore
EFlow = EntropyCore
OFlow = OptimizeCore
