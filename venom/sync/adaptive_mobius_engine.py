"""
Adaptive Möbius Engine - Temporal compression with hardware adaptation

Implements the Λ-TAS (Lambda Temporal Adaptive System) for VENOM Ω-AIOS.

Core Mathematical Foundation:
- T_parallel = T_sequential / S_Total
- S_Total = Θ(θ) × Λ × S_A
- θ = 0.3×H_CPU + 0.3×H_MEM + 0.4×H_TERM  [Range: 0-1]
- Θ(θ) = Adaptive Compression (piecewise function)
- Λ = lambda_wrap [10-832, adaptive]
- S_A = Amdahl's Law speedup
"""

import logging
import math
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of temporal compression calculation"""
    sequential_time: float
    parallel_time: float
    speedup: float
    theta: float
    theta_compression: float
    n_cores: int
    lambda_wrap: float
    parallel_fraction: float
    reduction_percent: float
    hardware_profile: Dict[str, Any]


class AdaptiveMobiusEngine:
    """
    Adaptive Möbius Engine for temporal compression
    
    Automatically configures based on hardware capabilities and
    applies adaptive temporal compression using the Möbius transformation.
    
    Modes:
    - UNWRAP: θ < 0.3 (low resources)
    - BALANCE: 0.5 ≤ θ < 0.7 (optimal)
    - WRAP: 0.7 ≤ θ < 0.9 (high performance)
    - OPTIMIZE: θ ≥ 0.9 (maximum performance)
    """
    
    LAMBDA_WRAP_MAX = 832.0
    LAMBDA_WRAP_MIN = 10.0
    
    # Theta thresholds
    THETA_UNWRAP = 0.3
    THETA_BALANCE_LOW = 0.5
    THETA_BALANCE_HIGH = 0.7
    THETA_WRAP_HIGH = 0.9
    
    def __init__(
        self,
        auto_detect: bool = True,
        override_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Adaptive Möbius Engine
        
        Args:
            auto_detect: Auto-detect hardware (requires UniversalHardwareScanner)
            override_config: Manual configuration override
                {
                    'n_cores': int,
                    'lambda_wrap': float,
                    'parallel_fraction': float,
                    'cpu_health': float,
                    'memory_health': float,
                    'thermal_health': float
                }
        """
        self.config = {}
        self.hardware_profile = {}
        
        if override_config:
            # Use manual configuration
            self.config = override_config
            logger.info("📐 Möbius Engine: Using manual configuration")
        elif auto_detect:
            # Auto-detect hardware
            try:
                from ..hardware.universal_scanner import UniversalHardwareScanner
                scanner = UniversalHardwareScanner()
                profile = scanner.scan()
                
                self.config = {
                    'n_cores': profile.optimal_workers,
                    'lambda_wrap': profile.lambda_wrap,
                    'parallel_fraction': profile.parallel_fraction,
                    'cpu_health': self._cpu_to_health(profile.cpu_usage_percent),
                    'memory_health': self._memory_to_health(profile.memory_usage_percent),
                    'thermal_health': self._thermal_to_health(profile.cpu_temperature)
                }
                self.hardware_profile = scanner.to_dict()
                
                logger.info(f"📐 Möbius Engine: Auto-configured for "
                           f"N={self.config['n_cores']}, "
                           f"Λ={self.config['lambda_wrap']:.1f}, "
                           f"P={self.config['parallel_fraction']:.3f}")
            except Exception as e:
                logger.warning(f"Auto-detection failed: {e}. Using defaults.")
                self._set_defaults()
        else:
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration"""
        self.config = {
            'n_cores': 4,
            'lambda_wrap': 200.0,
            'parallel_fraction': 0.75,
            'cpu_health': 0.7,
            'memory_health': 0.7,
            'thermal_health': 0.8
        }
        logger.info("📐 Möbius Engine: Using default configuration")
    
    def _cpu_to_health(self, usage_percent: float) -> float:
        """Convert CPU usage to health score [0-1]"""
        # 0% usage = 1.0 health, 100% usage = 0.0 health
        return max(0.0, min(1.0, 1.0 - (usage_percent / 100.0)))
    
    def _memory_to_health(self, usage_percent: float) -> float:
        """Convert memory usage to health score [0-1]"""
        # 0% usage = 1.0 health, 100% usage = 0.0 health
        return max(0.0, min(1.0, 1.0 - (usage_percent / 100.0)))
    
    def _thermal_to_health(self, temperature: Optional[float]) -> float:
        """Convert temperature to health score [0-1]"""
        if temperature is None:
            return 0.8  # Default if temperature unknown
        
        # Thermal mapping:
        # < 50°C: 1.0
        # 50-70°C: linear decrease to 0.5
        # 70-90°C: linear decrease to 0.0
        # > 90°C: 0.0
        if temperature < 50:
            return 1.0
        elif temperature < 70:
            return 1.0 - ((temperature - 50) / 40.0)  # 1.0 → 0.5
        elif temperature < 90:
            return 0.5 - ((temperature - 70) / 40.0)  # 0.5 → 0.0
        else:
            return 0.0
    
    def calculate_theta(
        self,
        cpu_health: Optional[float] = None,
        memory_health: Optional[float] = None,
        thermal_health: Optional[float] = None
    ) -> float:
        """
        Calculate system health theta (θ)
        
        Formula: θ = 0.3×H_CPU + 0.3×H_MEM + 0.4×H_TERM
        
        Args:
            cpu_health: CPU health [0-1], optional
            memory_health: Memory health [0-1], optional
            thermal_health: Thermal health [0-1], optional
            
        Returns:
            Theta value [0-1]
        """
        h_cpu = cpu_health if cpu_health is not None else self.config.get('cpu_health', 0.7)
        h_mem = memory_health if memory_health is not None else self.config.get('memory_health', 0.7)
        h_term = thermal_health if thermal_health is not None else self.config.get('thermal_health', 0.8)
        
        theta = 0.3 * h_cpu + 0.3 * h_mem + 0.4 * h_term
        theta = max(0.0, min(1.0, theta))
        
        return theta
    
    def theta_compression(
        self,
        theta: float,
        mode: str = 'adaptive'
    ) -> float:
        """
        Calculate Θ(θ) - adaptive compression factor
        
        Piecewise function:
        - θ < 0.3:        Θ = 0.5 (UNWRAP)
        - 0.3 ≤ θ < 0.5:  Θ = 0.5 + (θ-0.3)×2.5
        - 0.5 ≤ θ < 0.7:  Θ = 1.0 + (θ-0.5)×5.0 (BALANCE)
        - 0.7 ≤ θ < 0.9:  Θ = 2.0 + (θ-0.7)×2.5 (WRAP)
        - θ ≥ 0.9:        Θ = 3.0 (OPTIMIZE)
        
        Args:
            theta: System health [0-1]
            mode: Compression mode ('adaptive', 'conservative', 'aggressive')
            
        Returns:
            Compression factor Θ(θ)
        """
        if mode == 'conservative':
            # More conservative compression
            multiplier = 0.75
        elif mode == 'aggressive':
            # More aggressive compression
            multiplier = 1.25
        else:
            # Adaptive (standard)
            multiplier = 1.0
        
        # Piecewise compression function
        if theta < self.THETA_UNWRAP:
            # UNWRAP mode
            theta_comp = 0.5
        elif theta < self.THETA_BALANCE_LOW:
            # Transition to BALANCE
            theta_comp = 0.5 + (theta - self.THETA_UNWRAP) * 2.5
        elif theta < self.THETA_BALANCE_HIGH:
            # BALANCE mode
            theta_comp = 1.0 + (theta - self.THETA_BALANCE_LOW) * 5.0
        elif theta < self.THETA_WRAP_HIGH:
            # WRAP mode
            theta_comp = 2.0 + (theta - self.THETA_BALANCE_HIGH) * 2.5
        else:
            # OPTIMIZE mode
            theta_comp = 3.0
        
        # Apply mode multiplier
        theta_comp *= multiplier
        
        return theta_comp
    
    def amdahl_speedup(
        self,
        n_cores: Optional[int] = None,
        parallel_fraction: Optional[float] = None
    ) -> float:
        """
        Calculate Amdahl's Law speedup (S_A)
        
        Formula: S_A = 1 / [(1-P) + P/N]
        
        Args:
            n_cores: Number of cores (N)
            parallel_fraction: Parallel fraction (P)
            
        Returns:
            Amdahl speedup
        """
        N = n_cores if n_cores is not None else self.config.get('n_cores', 4)
        P = parallel_fraction if parallel_fraction is not None else self.config.get('parallel_fraction', 0.75)
        
        # Amdahl's Law
        s_a = 1.0 / ((1.0 - P) + (P / N))
        
        return s_a
    
    def total_speedup(
        self,
        theta: Optional[float] = None,
        theta_mode: str = 'adaptive'
    ) -> float:
        """
        Calculate total speedup (S_Total)
        
        Formula: S_Total = Θ(θ) × Λ × S_A
        
        Args:
            theta: System health [0-1], calculated if None
            theta_mode: Compression mode
            
        Returns:
            Total speedup factor
        """
        # Calculate theta if not provided
        if theta is None:
            theta = self.calculate_theta()
        
        # Get compression factor
        theta_comp = self.theta_compression(theta, mode=theta_mode)
        
        # Get lambda wrap
        lambda_wrap = self.config.get('lambda_wrap', 200.0)
        
        # Get Amdahl speedup
        s_a = self.amdahl_speedup()
        
        # Calculate total speedup
        s_total = theta_comp * lambda_wrap * s_a
        
        return s_total
    
    def compress_time(
        self,
        sequential_time: float,
        theta: Optional[float] = None,
        theta_mode: str = 'adaptive'
    ) -> CompressionResult:
        """
        Compress sequential time to parallel time
        
        Formula: T_parallel = T_sequential / S_Total
        
        Args:
            sequential_time: Sequential execution time (hours)
            theta: System health [0-1], auto-calculated if None
            theta_mode: Compression mode
            
        Returns:
            CompressionResult with detailed breakdown
        """
        # Calculate theta if not provided
        if theta is None:
            theta = self.calculate_theta()
        
        # Get compression factor
        theta_comp = self.theta_compression(theta, mode=theta_mode)
        
        # Get parameters
        n_cores = self.config.get('n_cores', 4)
        lambda_wrap = self.config.get('lambda_wrap', 200.0)
        parallel_fraction = self.config.get('parallel_fraction', 0.75)
        
        # Calculate Amdahl speedup
        s_a = self.amdahl_speedup(n_cores, parallel_fraction)
        
        # Calculate total speedup
        s_total = theta_comp * lambda_wrap * s_a
        
        # Calculate parallel time
        parallel_time = sequential_time / s_total
        
        # Calculate reduction
        reduction_percent = ((sequential_time - parallel_time) / sequential_time) * 100
        
        logger.info(f"⚡ Temporal Compression: {sequential_time:.1f}h → {parallel_time:.2f}h "
                   f"(speedup: {s_total:.1f}x, reduction: {reduction_percent:.1f}%)")
        
        return CompressionResult(
            sequential_time=sequential_time,
            parallel_time=parallel_time,
            speedup=s_total,
            theta=theta,
            theta_compression=theta_comp,
            n_cores=n_cores,
            lambda_wrap=lambda_wrap,
            parallel_fraction=parallel_fraction,
            reduction_percent=reduction_percent,
            hardware_profile=self.hardware_profile
        )
    
    def get_mode_name(self, theta: float) -> str:
        """Get compression mode name for theta value"""
        if theta < self.THETA_UNWRAP:
            return "UNWRAP"
        elif theta < self.THETA_BALANCE_LOW:
            return "TRANSITION"
        elif theta < self.THETA_BALANCE_HIGH:
            return "BALANCE"
        elif theta < self.THETA_WRAP_HIGH:
            return "WRAP"
        else:
            return "OPTIMIZE"
    
    def print_compression_summary(self, result: CompressionResult):
        """Print human-readable compression summary"""
        print("\n" + "="*60)
        print("⚡ VENOM Ω-AIOS Temporal Compression Summary")
        print("="*60)
        
        print(f"\n⏱️  Execution Time:")
        print(f"  Sequential: {result.sequential_time:.2f} hours")
        print(f"  Parallel:   {result.parallel_time:.2f} hours")
        print(f"  Speedup:    {result.speedup:.1f}x")
        print(f"  Reduction:  {result.reduction_percent:.1f}%")
        
        print(f"\n📐 Möbius Parameters:")
        print(f"  θ (theta):            {result.theta:.3f} [{self.get_mode_name(result.theta)}]")
        print(f"  Θ(θ) (compression):   {result.theta_compression:.3f}")
        print(f"  N (cores):            {result.n_cores}")
        print(f"  Λ (lambda_wrap):      {result.lambda_wrap:.1f}")
        print(f"  P (parallel_fraction): {result.parallel_fraction:.3f}")
        
        # Calculate individual contributions
        s_a = self.amdahl_speedup(result.n_cores, result.parallel_fraction)
        print(f"\n🔍 Speedup Breakdown:")
        print(f"  Θ(θ) contribution:    {result.theta_compression:.3f}x")
        print(f"  Λ contribution:       {result.lambda_wrap:.1f}x")
        print(f"  Amdahl (S_A):         {s_a:.3f}x")
        print(f"  Total (Θ×Λ×S_A):      {result.speedup:.1f}x")
        
        print("="*60 + "\n")


def demo_compression():
    """Demo of temporal compression"""
    print("🌌 VENOM Ω-AIOS Adaptive Möbius Engine Demo\n")
    
    # Test different hardware profiles
    scenarios = [
        {
            'name': 'Raspberry Pi',
            'config': {
                'n_cores': 4,
                'lambda_wrap': 50.0,
                'parallel_fraction': 0.65,
                'cpu_health': 0.5,
                'memory_health': 0.6,
                'thermal_health': 0.7
            }
        },
        {
            'name': 'Laptop',
            'config': {
                'n_cores': 8,
                'lambda_wrap': 400.0,
                'parallel_fraction': 0.80,
                'cpu_health': 0.7,
                'memory_health': 0.8,
                'thermal_health': 0.8
            }
        },
        {
            'name': 'Cloud Server',
            'config': {
                'n_cores': 32,
                'lambda_wrap': 832.0,
                'parallel_fraction': 0.95,
                'cpu_health': 0.9,
                'memory_health': 0.95,
                'thermal_health': 0.9
            }
        }
    ]
    
    sequential_time = 840.0  # 840 hours (35 days)
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"📱 Scenario: {scenario['name']}")
        print(f"{'='*60}")
        
        engine = AdaptiveMobiusEngine(
            auto_detect=False,
            override_config=scenario['config']
        )
        
        result = engine.compress_time(sequential_time)
        engine.print_compression_summary(result)


if __name__ == "__main__":
    # Run demo
    demo_compression()
