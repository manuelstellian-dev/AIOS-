"""
Omega Arbiter - Enhanced Arbiter with Möbius Engine integration

Extends the base Arbiter with:
- Adaptive Möbius temporal compression
- Real-time theta monitoring
- Parallel wave execution
- Adaptive throttling based on system health
"""

import logging
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .arbiter import Arbiter
from ..sync.pulse import TLambdaPulse
from ..control.genomic_pid import GenomicPID
from ..inference.entropy_model import EntropyModel
from ..ledger.immutable_ledger import ImmutableLedger
from ..mesh.p2p import P2PMesh

logger = logging.getLogger(__name__)


class OmegaArbiter(Arbiter):
    """
    Omega Arbiter - Enhanced Arbiter with Möbius integration
    
    Features:
    - Adaptive temporal compression via Möbius Engine
    - Real-time theta monitoring
    - Parallel wave execution with λ-wrapping
    - Adaptive throttling based on system health (θ)
    - Backward compatible with base Arbiter
    """
    
    def __init__(
        self,
        pulse: Optional[TLambdaPulse] = None,
        pid: Optional[GenomicPID] = None,
        entropy_model: Optional[EntropyModel] = None,
        ledger: Optional[ImmutableLedger] = None,
        mesh: Optional[P2PMesh] = None,
        mobius_engine=None,
        theta_monitor=None,
        enable_omega: bool = True
    ):
        """
        Initialize Omega Arbiter
        
        Args:
            pulse: T_Λ pulse generator
            pid: Genomic PID controller
            entropy_model: Entropy inference model
            ledger: Immutable ledger
            mesh: P2P mesh network
            mobius_engine: AdaptiveMobiusEngine instance (optional, auto-created)
            theta_monitor: ThetaMonitor instance (optional, auto-created)
            enable_omega: Enable Ω features (False for backward compatibility)
        """
        # Initialize base Arbiter
        super().__init__(pulse, pid, entropy_model, ledger, mesh)
        
        self.enable_omega = enable_omega
        
        if not enable_omega:
            logger.info("🔵 OmegaArbiter: Running in legacy mode (Ω features disabled)")
            self.mobius_engine = None
            self.theta_monitor = None
            return
        
        # Initialize Möbius Engine
        if mobius_engine is None:
            try:
                from ..sync.adaptive_mobius_engine import AdaptiveMobiusEngine
                self.mobius_engine = AdaptiveMobiusEngine(auto_detect=True)
                logger.info("⚡ OmegaArbiter: Möbius Engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Möbius Engine: {e}")
                self.mobius_engine = None
        else:
            self.mobius_engine = mobius_engine
        
        # Initialize Theta Monitor
        if theta_monitor is None:
            try:
                from ..observability.theta_monitor import ThetaMonitor
                self.theta_monitor = ThetaMonitor(interval=1.0)
                self.theta_monitor.start_monitoring()
                logger.info("📊 OmegaArbiter: Theta Monitor started")
            except Exception as e:
                logger.warning(f"Could not initialize Theta Monitor: {e}")
                self.theta_monitor = None
        else:
            self.theta_monitor = theta_monitor
            if not theta_monitor.running:
                theta_monitor.start_monitoring()
        
        # Wave execution state
        self.wave_results = {}
        self.current_theta = 0.0
        self.adaptive_throttle_enabled = True
        
        logger.info("🌌 OmegaArbiter: Initialized with Ω-AIOS capabilities")
    
    def execute_wave_parallel(
        self,
        wave: Dict[str, Any],
        theta: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a single wave with Möbius compression
        
        Args:
            wave: Wave definition with tasks
            theta: System health (auto-detected if None)
            
        Returns:
            Wave execution result
        """
        wave_id = wave.get('id', 'unknown')
        tasks = wave.get('tasks', [])
        
        if theta is None and self.theta_monitor:
            theta = self.theta_monitor.current_theta
        
        logger.info(f"🌊 Executing Wave {wave_id} with {len(tasks)} tasks (θ={theta:.3f})")
        
        start_time = time.time()
        
        # Execute tasks in parallel
        task_results = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {
                executor.submit(self._execute_task, task, theta): task
                for task in tasks
            }
            
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    task_results.append(result)
                except Exception as e:
                    logger.error(f"Task {task.get('name', 'unknown')} failed: {e}")
                    task_results.append({
                        'task': task.get('name', 'unknown'),
                        'status': 'failed',
                        'error': str(e)
                    })
        
        execution_time = time.time() - start_time
        
        # Calculate compression if Möbius engine available
        compression_info = {}
        if self.mobius_engine and theta is not None:
            compression_factor = self.mobius_engine.theta_compression(theta)
            compression_info = {
                'theta': theta,
                'compression_factor': compression_factor,
                'estimated_sequential_time': execution_time * compression_factor
            }
        
        result = {
            'wave_id': wave_id,
            'status': 'completed',
            'tasks_total': len(tasks),
            'tasks_succeeded': len([r for r in task_results if r.get('status') == 'success']),
            'tasks_failed': len([r for r in task_results if r.get('status') == 'failed']),
            'execution_time': execution_time,
            'task_results': task_results,
            'compression_info': compression_info
        }
        
        logger.info(f"✅ Wave {wave_id} completed in {execution_time:.2f}s")
        
        return result
    
    def _execute_task(
        self,
        task: Dict[str, Any],
        theta: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a single task (internal)"""
        task_name = task.get('name', 'unknown')
        task_fn = task.get('function')
        
        if task_fn is None:
            # Mock execution for demo/testing
            time.sleep(0.1)
            return {
                'task': task_name,
                'status': 'success',
                'result': f'Mock result for {task_name}'
            }
        
        try:
            result = task_fn()
            return {
                'task': task_name,
                'status': 'success',
                'result': result
            }
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            return {
                'task': task_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def execute_all_waves_parallel(
        self,
        waves: List[Dict[str, Any]],
        adaptive_throttle: bool = True
    ) -> Dict[str, Any]:
        """
        Execute all waves in parallel with adaptive throttling
        
        Args:
            waves: List of wave definitions
            adaptive_throttle: Enable adaptive throttling based on θ
            
        Returns:
            Aggregate execution results
        """
        logger.info(f"🌊🌊🌊 Executing {len(waves)} waves in parallel")
        
        start_time = time.time()
        wave_results = []
        
        # Determine parallelism based on theta
        max_parallel = len(waves)
        if adaptive_throttle and self.theta_monitor:
            theta = self.theta_monitor.current_theta
            if theta < 0.3:
                max_parallel = max(1, len(waves) // 4)
            elif theta < 0.5:
                max_parallel = max(1, len(waves) // 2)
            elif theta < 0.7:
                max_parallel = max(1, int(len(waves) * 0.75))
            
            logger.info(f"📊 Adaptive throttle: θ={theta:.3f}, parallel={max_parallel}/{len(waves)}")
        
        # Execute waves in parallel
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(self.execute_wave_parallel, wave): wave
                for wave in waves
            }
            
            for future in as_completed(futures):
                wave = futures[future]
                try:
                    result = future.result()
                    wave_results.append(result)
                except Exception as e:
                    logger.error(f"Wave {wave.get('id', 'unknown')} failed: {e}")
                    wave_results.append({
                        'wave_id': wave.get('id', 'unknown'),
                        'status': 'failed',
                        'error': str(e)
                    })
        
        total_time = time.time() - start_time
        
        # Calculate overall statistics
        total_tasks = sum(r.get('tasks_total', 0) for r in wave_results)
        succeeded_tasks = sum(r.get('tasks_succeeded', 0) for r in wave_results)
        failed_tasks = sum(r.get('tasks_failed', 0) for r in wave_results)
        
        result = {
            'status': 'completed',
            'waves_total': len(waves),
            'waves_succeeded': len([r for r in wave_results if r.get('status') == 'completed']),
            'waves_failed': len([r for r in wave_results if r.get('status') == 'failed']),
            'tasks_total': total_tasks,
            'tasks_succeeded': succeeded_tasks,
            'tasks_failed': failed_tasks,
            'total_execution_time': total_time,
            'wave_results': wave_results
        }
        
        logger.info(f"✅ All waves completed in {total_time:.2f}s "
                   f"({succeeded_tasks}/{total_tasks} tasks succeeded)")
        
        return result
    
    def adaptive_throttle(self, current_theta: float) -> Dict[str, Any]:
        """
        Adjust execution based on current theta
        
        Args:
            current_theta: Current system health θ
            
        Returns:
            Throttle configuration
        """
        if current_theta >= 0.9:
            mode = "OPTIMIZE"
            delay_factor = 0.0
            max_parallel_factor = 1.0
        elif current_theta >= 0.7:
            mode = "WRAP"
            delay_factor = 0.1
            max_parallel_factor = 0.9
        elif current_theta >= 0.5:
            mode = "BALANCE"
            delay_factor = 0.2
            max_parallel_factor = 0.75
        elif current_theta >= 0.3:
            mode = "TRANSITION"
            delay_factor = 0.5
            max_parallel_factor = 0.5
        else:
            mode = "UNWRAP"
            delay_factor = 1.0
            max_parallel_factor = 0.25
        
        return {
            'mode': mode,
            'theta': current_theta,
            'delay_factor': delay_factor,
            'max_parallel_factor': max_parallel_factor
        }
    
    def start_omega(
        self,
        waves: Optional[List[Dict[str, Any]]] = None,
        beats: int = -1,
        execute_waves: bool = True
    ):
        """
        Start Omega Arbiter with optional wave execution
        
        Args:
            waves: Optional list of waves to execute
            beats: Number of beats to run (-1 for infinite)
            execute_waves: Execute waves before starting beat loop
        """
        logger.info("🌌 Starting VENOM Ω-AIOS...")
        
        # Execute waves if provided
        if execute_waves and waves:
            wave_result = self.execute_all_waves_parallel(waves)
            self.wave_results = wave_result
            logger.info(f"✅ Wave execution completed: "
                       f"{wave_result['waves_succeeded']}/{wave_result['waves_total']} waves")
        
        # Start normal Arbiter beat loop
        if beats != 0:
            logger.info(f"▶️  Starting Arbiter beat loop (beats={beats})...")
            self.start(beats)
    
    def get_omega_status(self) -> Dict[str, Any]:
        """
        Get Omega Arbiter status
        
        Returns:
            Status dictionary with all metrics
        """
        status = {
            'omega_enabled': self.enable_omega,
            'beat_count': self.beat_count,
            'running': self.running
        }
        
        if self.enable_omega:
            # Add theta metrics
            if self.theta_monitor:
                status['theta_metrics'] = self.theta_monitor.get_current_metrics()
            
            # Add Möbius info
            if self.mobius_engine:
                status['mobius_config'] = self.mobius_engine.config
            
            # Add wave results
            if self.wave_results:
                status['wave_results'] = {
                    'waves_succeeded': self.wave_results.get('waves_succeeded', 0),
                    'waves_total': self.wave_results.get('waves_total', 0),
                    'tasks_succeeded': self.wave_results.get('tasks_succeeded', 0),
                    'tasks_total': self.wave_results.get('tasks_total', 0),
                    'execution_time': self.wave_results.get('total_execution_time', 0)
                }
        
        return status
    
    def stop(self):
        """Stop Omega Arbiter and cleanup"""
        super().stop()
        
        if self.enable_omega and self.theta_monitor:
            self.theta_monitor.stop_monitoring()
            logger.info("📊 Theta Monitor stopped")


def demo_omega_arbiter():
    """Demo of Omega Arbiter"""
    print("🌌 VENOM Ω-AIOS Omega Arbiter Demo\n")
    
    # Create demo waves
    waves = [
        {
            'id': 'wave-5',
            'name': 'AI/ML Registry',
            'tasks': [
                {'name': 'transformer_bridge', 'function': None},
                {'name': 'vision_models', 'function': None},
                {'name': 'automl', 'function': None}
            ]
        },
        {
            'id': 'wave-6',
            'name': 'Hardware Bridges',
            'tasks': [
                {'name': 'rocm_bridge', 'function': None},
                {'name': 'metal_bridge', 'function': None},
                {'name': 'oneapi_bridge', 'function': None}
            ]
        },
        {
            'id': 'wave-7',
            'name': 'Multi-Cloud',
            'tasks': [
                {'name': 'aws_deployer', 'function': None},
                {'name': 'azure_deployer', 'function': None},
                {'name': 'gcp_deployer', 'function': None}
            ]
        }
    ]
    
    # Create Omega Arbiter
    arbiter = OmegaArbiter(enable_omega=True)
    
    # Execute waves
    result = arbiter.execute_all_waves_parallel(waves)
    
    print("\n" + "="*60)
    print("📊 Execution Results:")
    print("="*60)
    print(f"Waves: {result['waves_succeeded']}/{result['waves_total']} succeeded")
    print(f"Tasks: {result['tasks_succeeded']}/{result['tasks_total']} succeeded")
    print(f"Time: {result['total_execution_time']:.2f}s")
    print("="*60 + "\n")
    
    # Get status
    status = arbiter.get_omega_status()
    print("Status:", status)
    
    # Cleanup
    arbiter.stop()


if __name__ == "__main__":
    demo_omega_arbiter()
