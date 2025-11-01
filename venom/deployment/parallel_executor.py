"""
Parallel Wave Executor - Execute waves with dependency management and λ-wrapping

Features:
- Wave decomposition into micro-tasks
- Dependency graph construction
- Parallel execution with topological sorting
- Adaptive λ-wrapping based on Möbius engine
- Progress tracking and failure handling
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MicroTask:
    """Micro-task unit for parallel execution"""
    id: str
    name: str
    wave_id: str
    function: Optional[Callable]
    dependencies: List[str]
    lambda_factor: float = 1.0
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ExecutionResult:
    """Result of parallel wave execution"""
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    skipped_tasks: int
    total_time: float
    tasks: List[MicroTask]
    speedup: float = 1.0
    compression_info: Dict[str, Any] = None


@dataclass
class ProgressReport:
    """Real-time progress report"""
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    skipped_tasks: int
    progress_percent: float
    elapsed_time: float
    estimated_remaining_time: Optional[float] = None


class ParallelWaveExecutor:
    """
    Parallel Wave Executor with dependency management
    
    Decomposes waves into micro-tasks, builds dependency graph,
    and executes tasks in parallel with adaptive λ-wrapping.
    """
    
    def __init__(
        self,
        mobius_engine=None,
        theta_monitor=None,
        n_workers: Optional[int] = None
    ):
        """
        Initialize Parallel Wave Executor
        
        Args:
            mobius_engine: AdaptiveMobiusEngine instance (optional)
            theta_monitor: ThetaMonitor instance (optional)
            n_workers: Number of workers (auto-detected if None)
        """
        self.mobius_engine = mobius_engine
        self.theta_monitor = theta_monitor
        
        # Determine worker count
        if n_workers is None:
            if mobius_engine and hasattr(mobius_engine, 'config'):
                self.n_workers = mobius_engine.config.get('n_cores', 4)
            else:
                try:
                    import psutil
                    self.n_workers = psutil.cpu_count(logical=True) or 4
                except:
                    self.n_workers = 4
        else:
            self.n_workers = n_workers
        
        # Execution state
        self.tasks: Dict[str, MicroTask] = {}
        self.dependency_graph = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        logger.info(f"⚡ ParallelWaveExecutor: Initialized with {self.n_workers} workers")
    
    def decompose_wave(
        self,
        wave: Dict[str, Any],
        lambda_factor: Optional[float] = None
    ) -> List[MicroTask]:
        """
        Decompose wave into micro-tasks
        
        Args:
            wave: Wave definition
            lambda_factor: Lambda wrapping factor (from Möbius engine)
            
        Returns:
            List of MicroTask objects
        """
        wave_id = wave.get('id', 'unknown')
        wave_tasks = wave.get('tasks', [])
        
        # Determine lambda factor
        if lambda_factor is None and self.mobius_engine:
            lambda_factor = self.mobius_engine.config.get('lambda_wrap', 1.0)
        elif lambda_factor is None:
            lambda_factor = 1.0
        
        # Normalize lambda to task-level factor (typically < 10)
        task_lambda = min(10.0, lambda_factor / max(1, len(wave_tasks)))
        
        micro_tasks = []
        for idx, task_def in enumerate(wave_tasks):
            task_id = f"{wave_id}_{idx}_{task_def.get('name', 'task')}"
            
            micro_task = MicroTask(
                id=task_id,
                name=task_def.get('name', f'task_{idx}'),
                wave_id=wave_id,
                function=task_def.get('function'),
                dependencies=task_def.get('dependencies', []),
                lambda_factor=task_lambda
            )
            
            micro_tasks.append(micro_task)
            self.tasks[task_id] = micro_task
        
        logger.info(f"📦 Decomposed wave {wave_id} into {len(micro_tasks)} micro-tasks "
                   f"(λ={task_lambda:.2f})")
        
        return micro_tasks
    
    def build_dependency_graph(
        self,
        waves: List[Dict[str, Any]]
    ):
        """
        Build dependency graph from waves
        
        Uses networkx for topological sorting and cycle detection.
        
        Args:
            waves: List of wave definitions
        """
        try:
            import networkx as nx
        except ImportError:
            logger.warning("networkx not available, using simple dependency tracking")
            self.dependency_graph = None
            return
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Decompose all waves
        all_tasks = []
        for wave in waves:
            tasks = self.decompose_wave(wave)
            all_tasks.extend(tasks)
        
        # Add nodes
        for task in all_tasks:
            G.add_node(task.id, task=task)
        
        # Add edges (dependencies)
        for task in all_tasks:
            for dep in task.dependencies:
                # Find dependency task
                dep_task_id = None
                for t in all_tasks:
                    if t.name == dep or t.id == dep:
                        dep_task_id = t.id
                        break
                
                if dep_task_id:
                    G.add_edge(dep_task_id, task.id)
                else:
                    logger.warning(f"Dependency '{dep}' not found for task {task.id}")
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(G):
            cycles = list(nx.simple_cycles(G))
            logger.error(f"❌ Dependency graph contains cycles: {cycles}")
            raise ValueError("Dependency graph contains cycles")
        
        self.dependency_graph = G
        logger.info(f"📊 Dependency graph built: {len(G.nodes)} nodes, {len(G.edges)} edges")
    
    def _get_ready_tasks(self) -> List[MicroTask]:
        """Get tasks that are ready to execute (all dependencies completed)"""
        ready = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            deps_ready = True
            for dep in task.dependencies:
                # Find dependency task
                dep_task = None
                for t in self.tasks.values():
                    if t.name == dep or t.id == dep:
                        dep_task = t
                        break
                
                if dep_task and dep_task.status != TaskStatus.COMPLETED:
                    deps_ready = False
                    break
            
            if deps_ready:
                ready.append(task)
        
        return ready
    
    def _execute_task(self, task: MicroTask) -> MicroTask:
        """Execute a single micro-task"""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        logger.debug(f"▶️  Executing task: {task.name} (λ={task.lambda_factor:.2f})")
        
        try:
            if task.function is None:
                # Mock execution for demo/testing
                # Simulate work time reduced by lambda factor
                work_time = 0.1 / task.lambda_factor
                time.sleep(work_time)
                task.result = f"Mock result for {task.name}"
            else:
                # Execute actual function
                task.result = task.function()
            
            task.status = TaskStatus.COMPLETED
            task.end_time = time.time()
            
            logger.debug(f"✅ Task completed: {task.name} "
                        f"({task.end_time - task.start_time:.3f}s)")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = time.time()
            
            logger.error(f"❌ Task failed: {task.name} - {e}")
        
        return task
    
    def execute_parallel(
        self,
        waves: List[Dict[str, Any]],
        adaptive_throttle: bool = True
    ) -> ExecutionResult:
        """
        Execute waves in parallel with dependency management
        
        Args:
            waves: List of wave definitions
            adaptive_throttle: Enable adaptive throttling based on θ
            
        Returns:
            ExecutionResult with execution statistics
        """
        logger.info(f"🚀 Starting parallel execution of {len(waves)} waves")
        
        self.start_time = time.time()
        
        # Build dependency graph
        try:
            self.build_dependency_graph(waves)
        except Exception as e:
            logger.error(f"Failed to build dependency graph: {e}")
            # Fall back to simple decomposition
            for wave in waves:
                self.decompose_wave(wave)
        
        # Adjust workers based on theta if adaptive throttling enabled
        max_workers = self.n_workers
        if adaptive_throttle and self.theta_monitor:
            theta = self.theta_monitor.current_theta
            if theta < 0.3:
                max_workers = max(1, self.n_workers // 4)
            elif theta < 0.5:
                max_workers = max(1, self.n_workers // 2)
            elif theta < 0.7:
                max_workers = max(1, int(self.n_workers * 0.75))
            
            logger.info(f"📊 Adaptive throttle: θ={theta:.3f}, workers={max_workers}/{self.n_workers}")
        
        # Execute tasks in waves based on dependencies
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            active_futures = {}
            
            while True:
                # Get ready tasks
                ready_tasks = self._get_ready_tasks()
                
                # Submit ready tasks
                for task in ready_tasks:
                    if task.id not in active_futures:
                        future = executor.submit(self._execute_task, task)
                        active_futures[task.id] = future
                
                # Wait for some tasks to complete
                if active_futures:
                    # Wait for at least one to complete
                    completed_futures = []
                    for task_id, future in list(active_futures.items()):
                        if future.done():
                            try:
                                future.result()
                            except Exception as e:
                                logger.error(f"Future error for {task_id}: {e}")
                            completed_futures.append(task_id)
                    
                    # Remove completed futures
                    for task_id in completed_futures:
                        del active_futures[task_id]
                    
                    # Check if all tasks are done
                    all_done = all(
                        t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]
                        for t in self.tasks.values()
                    )
                    
                    if all_done:
                        break
                    
                    # Small delay to avoid busy waiting
                    time.sleep(0.01)
                else:
                    # No active futures and no ready tasks
                    # Check if we're stuck
                    pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                    if pending:
                        logger.warning(f"⚠️  {len(pending)} tasks stuck in pending state")
                        # Mark them as skipped
                        for task in pending:
                            task.status = TaskStatus.SKIPPED
                    break
        
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        # Collect statistics
        completed = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        failed = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
        skipped = [t for t in self.tasks.values() if t.status == TaskStatus.SKIPPED]
        
        # Calculate speedup
        speedup = 1.0
        if self.mobius_engine:
            theta = self.theta_monitor.current_theta if self.theta_monitor else None
            speedup = self.mobius_engine.total_speedup(theta=theta)
        
        result = ExecutionResult(
            status='completed' if not failed else 'partial',
            total_tasks=len(self.tasks),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            skipped_tasks=len(skipped),
            total_time=total_time,
            tasks=list(self.tasks.values()),
            speedup=speedup
        )
        
        logger.info(f"✅ Parallel execution completed in {total_time:.2f}s")
        logger.info(f"📊 Results: {len(completed)} completed, {len(failed)} failed, "
                   f"{len(skipped)} skipped (speedup: {speedup:.1f}x)")
        
        return result
    
    def handle_task_failure(
        self,
        task: MicroTask,
        error: Exception,
        retry: bool = False
    ):
        """
        Handle task failure
        
        Args:
            task: Failed task
            error: Exception that caused failure
            retry: Whether to retry the task
        """
        logger.error(f"❌ Task {task.name} failed: {error}")
        
        if retry:
            logger.info(f"🔄 Retrying task {task.name}")
            task.status = TaskStatus.PENDING
            task.error = None
        else:
            # Mark dependent tasks as skipped
            for t in self.tasks.values():
                if task.id in t.dependencies or task.name in t.dependencies:
                    if t.status == TaskStatus.PENDING:
                        t.status = TaskStatus.SKIPPED
                        logger.warning(f"⏭️  Skipping dependent task {t.name}")
    
    def get_progress(self) -> ProgressReport:
        """
        Get current execution progress
        
        Returns:
            ProgressReport with current statistics
        """
        pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        running = [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
        completed = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        failed = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
        skipped = [t for t in self.tasks.values() if t.status == TaskStatus.SKIPPED]
        
        total = len(self.tasks)
        done = len(completed) + len(failed) + len(skipped)
        progress_percent = (done / total * 100) if total > 0 else 0
        
        elapsed_time = 0.0
        if self.start_time:
            elapsed_time = time.time() - self.start_time
        
        # Estimate remaining time
        estimated_remaining = None
        if len(completed) > 0 and elapsed_time > 0:
            avg_task_time = elapsed_time / len(completed)
            remaining_tasks = len(pending) + len(running)
            estimated_remaining = avg_task_time * remaining_tasks
        
        return ProgressReport(
            total_tasks=total,
            pending_tasks=len(pending),
            running_tasks=len(running),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            skipped_tasks=len(skipped),
            progress_percent=progress_percent,
            elapsed_time=elapsed_time,
            estimated_remaining_time=estimated_remaining
        )


def demo_parallel_executor():
    """Demo of parallel wave executor"""
    print("⚡ VENOM Ω-AIOS Parallel Wave Executor Demo\n")
    
    # Create demo waves with dependencies
    waves = [
        {
            'id': 'wave-foundation',
            'name': 'Foundation',
            'tasks': [
                {'name': 'init_system', 'function': None, 'dependencies': []},
                {'name': 'load_config', 'function': None, 'dependencies': ['init_system']}
            ]
        },
        {
            'id': 'wave-core',
            'name': 'Core Services',
            'tasks': [
                {'name': 'start_database', 'function': None, 'dependencies': ['load_config']},
                {'name': 'start_cache', 'function': None, 'dependencies': ['load_config']},
                {'name': 'start_queue', 'function': None, 'dependencies': ['load_config']}
            ]
        },
        {
            'id': 'wave-app',
            'name': 'Application',
            'tasks': [
                {'name': 'deploy_api', 'function': None, 'dependencies': ['start_database', 'start_cache']},
                {'name': 'deploy_worker', 'function': None, 'dependencies': ['start_queue']},
                {'name': 'deploy_ui', 'function': None, 'dependencies': ['deploy_api']}
            ]
        }
    ]
    
    # Create executor
    executor = ParallelWaveExecutor(n_workers=4)
    
    # Execute
    result = executor.execute_parallel(waves)
    
    # Print results
    print("\n" + "="*60)
    print("📊 Execution Results:")
    print("="*60)
    print(f"Total Tasks:     {result.total_tasks}")
    print(f"Completed:       {result.completed_tasks}")
    print(f"Failed:          {result.failed_tasks}")
    print(f"Skipped:         {result.skipped_tasks}")
    print(f"Execution Time:  {result.total_time:.2f}s")
    print(f"Speedup:         {result.speedup:.1f}x")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_parallel_executor()
