"""
Arbiter - The Brain and Orchestrator of VENOM Λ-GENESIS

Responsibilities:
- Parallel orchestration (time_wrap) using ThreadPoolExecutor with 4 workers
- Aggregation of recommendations from R, B, E, O cores
- Decision making based on threat thresholds and decision vector
- PID recalibration to adjust O weight and maintain stability (ΔV < 0)
"""
import logging
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

from ..flows.parallel_flows import RegenCore, BalanceCore, EntropyCore, OptimizeCore
from ..sync.pulse import TLambdaPulse
from ..control.genomic_pid import GenomicPID
from ..inference.entropy_model import EntropyModel
from ..ledger.immutable_ledger import ImmutableLedger
from ..mesh.p2p import P2PMesh
from .constants import Constants as C

logger = logging.getLogger(__name__)


class Action(Enum):
    """System actions"""
    QUARANTINE = "QUARANTINE"
    ALERT = "ALERT"
    APPLY_BALANCE = "APPLY_BALANCE"
    APPLY_OPTIMIZE = "APPLY_OPTIMIZE"
    NOOP = "NOOP"


class Arbiter:
    """
    Arbiter - The Decisional Brain orchestrating the fractal organism
    
    Implements:
    - time_wrap: Parallel execution of 4 cores (R, B, E, O) via ThreadPoolExecutor
    - aggregate_recommendations: Weighted aggregation using genome weights
    - decide: Action determination based on thresholds
    - recalibrate: PID-based O weight adjustment
    """
    
    def __init__(
        self,
        pulse: Optional[TLambdaPulse] = None,
        pid: Optional[GenomicPID] = None,
        entropy_model: Optional[EntropyModel] = None,
        ledger: Optional[ImmutableLedger] = None,
        mesh: Optional[P2PMesh] = None
    ):
        """
        Initialize Arbiter with all components
        
        Args:
            pulse: T_Λ pulse generator
            pid: Genomic PID controller
            entropy_model: Entropy inference model
            ledger: Immutable ledger
            mesh: P2P mesh network
        """
        # Core components
        self.pulse = pulse or TLambdaPulse()
        self.pid = pid or GenomicPID()
        self.entropy_model = entropy_model or EntropyModel()
        self.ledger = ledger or ImmutableLedger()
        self.mesh = mesh
        
        # Initialize cores (R, B, E, O)
        self.regen_core = RegenCore()
        self.balance_core = BalanceCore()
        self.entropy_core = EntropyCore(self.entropy_model)
        self.optimize_core = OptimizeCore()
        
        # ThreadPoolExecutor with 4 workers for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Genome (system state)
        self.genome = {
            "weights": {
                "R": 0.25,
                "B": 0.25,
                "E": 0.15,
                "O": 0.35
            },
            "risk": {
                "anoms": 0
            },
            "ml": {
                "ml_weight": 0.12
            }
        }
        
        self.beat_count = 0
        self.running = False
        
    def time_wrap(self, features: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Parallel execution of 4 cores using ThreadPoolExecutor
        This is the "fractal_parallel" pulse mechanism
        
        Args:
            features: Input features for cores
            
        Returns:
            Dictionary mapping core names to their results
        """
        cores = {
            "R": self.regen_core,
            "B": self.balance_core,
            "E": self.entropy_core,
            "O": self.optimize_core
        }
        
        # Submit all cores for parallel execution
        futures = {
            self.executor.submit(core.execute, self.genome, features): name
            for name, core in cores.items()
        }
        
        # Collect results
        results = {}
        for future in as_completed(futures):
            core_name = futures[future]
            try:
                result = future.result()
                results[core_name] = result
            except Exception as e:
                logger.error(f"Core {core_name} failed: {e}")
                results[core_name] = {"error": str(e)}
        
        return results
    
    def aggregate_recommendations(self, core_results: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Aggregate core recommendations using genome weights
        Creates the Decision Vector (decvec)
        
        Args:
            core_results: Results from all cores
            
        Returns:
            Decision vector with weighted aggregated values
        """
        weights = self.genome["weights"]
        
        # Extract values from cores
        r_urgency = core_results.get("R", {}).get("urgency", 0.0)
        b_conserve = core_results.get("B", {}).get("conserve", 0.0)
        e_threat = core_results.get("E", {}).get("threat_score", 0.0)
        o_gain = core_results.get("O", {}).get("expected_gain", 0.0)
        
        # Extract additional metrics
        r_cost = core_results.get("R", {}).get("cost", 0.0)
        
        # Weighted aggregation
        threat = e_threat * weights["E"]
        stability = b_conserve * weights["B"]
        repair_score = r_urgency * weights["R"]
        opt_gain = o_gain * weights["O"]
        
        decvec = {
            "threat": threat,
            "stability": stability,
            "repair_score": repair_score,
            "opt_gain": opt_gain,
            "raw_threat": e_threat,
            "raw_urgency": r_urgency,
            "raw_conserve": b_conserve,
            "raw_gain": o_gain
        }
        
        return decvec
    
    def decide(self, decvec: Dict[str, float]) -> Action:
        """
        Decision logic based on thresholds and decision vector
        
        Args:
            decvec: Decision vector from aggregation
            
        Returns:
            Action to take
        """
        threat = decvec["threat"]
        raw_threat = decvec["raw_threat"]
        stability = decvec["stability"]
        repair_score = decvec["repair_score"]
        opt_gain = decvec["opt_gain"]
        
        # Threat-based decisions (highest priority)
        if raw_threat >= C.THREAT_QUARANTINE:
            return Action.QUARANTINE
        
        if raw_threat >= C.THREAT_ALERT:
            return Action.ALERT
        
        # Balance-based decision
        if stability > C.STABILITY_THRESHOLD and repair_score < C.REPAIR_THRESHOLD:
            return Action.APPLY_BALANCE
        
        # Optimization-based decision
        if opt_gain > C.OPT_GAIN_THRESHOLD:
            return Action.APPLY_OPTIMIZE
        
        # Default: no operation
        return Action.NOOP
    
    def recalibrate(self, t_lambda: float) -> float:
        """
        PID recalibration to adjust O weight
        Maintains stability (ΔV < 0)
        
        Args:
            t_lambda: Current T_Λ value
            
        Returns:
            Weight adjustment applied to O
        """
        # Update PID parameters from BalanceCore if available
        if hasattr(self.balance_core, 'state'):
            state = self.balance_core.state
            if 'kp' in state:
                self.pid.update_params(state['kp'], state['ki'], state['kd'])
        
        # Compute PID output
        pid_result = self.pid.compute(t_lambda)
        
        # Extract weight adjustment
        weight_adjustment = pid_result["weight_adjustment"]
        
        # Apply adjustment to O weight
        old_o_weight = self.genome["weights"]["O"]
        new_o_weight = old_o_weight + weight_adjustment
        
        # Clamp O weight to reasonable bounds
        new_o_weight = max(0.1, min(0.9, new_o_weight))
        
        # Update genome
        self.genome["weights"]["O"] = new_o_weight
        
        # Normalize weights to sum to ~1.0
        self._normalize_weights()
        
        logger.debug(f"PID recalibration: O weight {old_o_weight:.4f} -> {new_o_weight:.4f} (Δ={weight_adjustment:.4f})")
        
        return weight_adjustment
    
    def _normalize_weights(self):
        """Normalize genome weights to sum to 1.0"""
        weights = self.genome["weights"]
        total = sum(weights.values())
        if total > 0:
            for key in weights:
                weights[key] /= total
    
    def execute_beat(self) -> Dict[str, Any]:
        """
        Execute one complete beat (pulse cycle)
        
        Returns:
            Beat execution summary
        """
        self.beat_count += 1
        
        # Generate T_Λ pulse
        pulse_data = self.pulse.generate_pulse()
        t_lambda = pulse_data["t_lambda"]
        
        # Record pulse in ledger
        self.ledger.record_pulse(pulse_data)
        
        # Prepare features
        features = {
            "t_lambda": t_lambda,
            "beat": self.beat_count
        }
        
        # Parallel execution of cores (time_wrap)
        core_results = self.time_wrap(features)
        
        # Record core results in ledger
        for core_name, result in core_results.items():
            self.ledger.record_flow_result(core_name, result)
        
        # Aggregate recommendations
        decvec = self.aggregate_recommendations(core_results)
        
        # Make decision
        action = self.decide(decvec)
        
        # Record action in ledger
        self.ledger.record_action(action.value, decvec)
        
        # PID recalibration
        weight_adjustment = self.recalibrate(t_lambda)
        
        # Hybrid feedback for E weight (from specification)
        self._update_e_weight(decvec["raw_threat"], t_lambda)
        
        beat_summary = {
            "beat": self.beat_count,
            "t_lambda": t_lambda,
            "action": action.value,
            "decvec": decvec,
            "weights": dict(self.genome["weights"]),
            "weight_adjustment": weight_adjustment,
            "pid_stable": self.pid.is_stable(),
            "ledger_length": self.ledger.get_chain_length()
        }
        
        return beat_summary
    
    def _update_e_weight(self, threat: float, t_lambda: float):
        """
        Hybrid feedback for E weight
        Formula: E = 0.15 * threat * e^(-t/50) * (1 - O/0.3) if threat > 0.5, else E = 0.10
        """
        o_weight = self.genome["weights"]["O"]
        
        if threat > 0.5:
            # Time-based decay
            decay = math.exp(-self.beat_count / 50.0)
            # O-based factor
            o_factor = max(0.0, 1.0 - o_weight / 0.3)
            # New E weight
            e_weight = 0.15 * threat * decay * o_factor
        else:
            e_weight = 0.10
        
        # Clamp and update
        e_weight = max(0.05, min(0.30, e_weight))
        self.genome["weights"]["E"] = e_weight
        
        # Normalize
        self._normalize_weights()
    
    def start(self, beats: int = -1):
        """
        Start the Arbiter execution loop
        
        Args:
            beats: Number of beats to execute (-1 for infinite)
        """
        self.running = True
        logger.info(f"Arbiter starting with {beats} beats")
        
        beat_num = 0
        while self.running:
            if beats > 0 and beat_num >= beats:
                break
            
            try:
                summary = self.execute_beat()
                logger.info(f"Beat {summary['beat']}: Action={summary['action']}, T_Λ={summary['t_lambda']:.6f}")
                
                # Sleep for T_Λ duration
                delay = self.pulse.get_next_pulse_delay()
                time.sleep(delay)
                
                beat_num += 1
                
            except KeyboardInterrupt:
                logger.info("Arbiter interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in beat execution: {e}")
                if beats > 0:
                    break
        
        self.stop()
    
    def stop(self):
        """Stop the Arbiter"""
        self.running = False
        self.executor.shutdown(wait=True)
        if self.mesh:
            self.mesh.stop()
        logger.info("Arbiter stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "beat": self.beat_count,
            "running": self.running,
            "genome": self.genome,
            "pid_stable": self.pid.is_stable(),
            "ledger_length": self.ledger.get_chain_length(),
            "ledger_verified": self.ledger.verify_chain()
        }
