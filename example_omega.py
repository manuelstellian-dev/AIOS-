#!/usr/bin/env python3
"""
VENOM Ω-AIOS Example - Complete demonstration of universal adaptive system

This example shows:
1. Hardware scanning and auto-configuration
2. Temporal compression calculation
3. Parallel wave execution with adaptive throttling
4. Real-time theta monitoring
5. Omega Arbiter with Möbius integration
"""

import sys
import time


def example_1_hardware_scan():
    """Example 1: Hardware scanning"""
    print("="*70)
    print("Example 1: Universal Hardware Scanner")
    print("="*70)
    
    try:
        from venom.hardware.universal_scanner import UniversalHardwareScanner
        
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        scanner.print_profile()
        
        print(f"\n✅ Hardware scan completed successfully!")
        print(f"   Your system will use {profile.optimal_workers} workers")
        print(f"   Lambda wrap: {profile.lambda_wrap:.1f}")
        print(f"   Parallel fraction: {profile.parallel_fraction:.3f}")
        
        return profile
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil")
        return None


def example_2_temporal_compression(profile=None):
    """Example 2: Temporal compression"""
    print("\n" + "="*70)
    print("Example 2: Adaptive Möbius Engine - Temporal Compression")
    print("="*70)
    
    try:
        from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine
        
        # Use hardware profile if available
        if profile:
            config = {
                'n_cores': profile.optimal_workers,
                'lambda_wrap': profile.lambda_wrap,
                'parallel_fraction': profile.parallel_fraction,
                'cpu_health': 0.8,
                'memory_health': 0.85,
                'thermal_health': 0.9
            }
            engine = AdaptiveMobiusEngine(auto_detect=False, override_config=config)
            print(f"Using detected hardware configuration")
        else:
            engine = AdaptiveMobiusEngine(auto_detect=True)
            print(f"Using auto-detected configuration")
        
        # Calculate compression for 840 hours (35 days)
        sequential_time = 840.0
        result = engine.compress_time(sequential_time)
        
        engine.print_compression_summary(result)
        
        print(f"✅ Temporal compression calculated!")
        print(f"   840 hours → {result.parallel_time:.2f} hours")
        print(f"   That's a {result.speedup:.1f}x speedup!")
        
        return engine
    except ImportError as e:
        print(f"❌ Error: {e}")
        return None


def example_3_theta_monitoring():
    """Example 3: Real-time theta monitoring"""
    print("\n" + "="*70)
    print("Example 3: Theta Monitor - Real-time System Health")
    print("="*70)
    
    try:
        from venom.observability.theta_monitor import ThetaMonitor
        
        print("Starting theta monitor for 5 seconds...")
        monitor = ThetaMonitor(interval=0.5)
        monitor.start_monitoring()
        
        # Monitor for 5 seconds
        for i in range(3):
            time.sleep(1.5)
            monitor.print_status()
        
        monitor.stop_monitoring()
        
        print(f"\n✅ Monitoring complete!")
        metrics = monitor.get_current_metrics()
        print(f"   Final theta: {metrics['theta']:.3f}")
        print(f"   Compression factor: {metrics['compression_factor']:.3f}")
        
        return monitor
    except ImportError as e:
        print(f"❌ Error: {e}")
        return None


def example_4_parallel_execution():
    """Example 4: Parallel wave execution"""
    print("\n" + "="*70)
    print("Example 4: Parallel Wave Executor - Dependency-aware Execution")
    print("="*70)
    
    try:
        from venom.deployment.parallel_executor import ParallelWaveExecutor
        
        # Create test waves with dependencies
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
                'id': 'wave-services',
                'name': 'Core Services',
                'tasks': [
                    {'name': 'start_database', 'function': None, 'dependencies': ['load_config']},
                    {'name': 'start_cache', 'function': None, 'dependencies': ['load_config']},
                    {'name': 'start_queue', 'function': None, 'dependencies': ['load_config']}
                ]
            },
            {
                'id': 'wave-application',
                'name': 'Application Layer',
                'tasks': [
                    {'name': 'deploy_api', 'function': None, 'dependencies': ['start_database', 'start_cache']},
                    {'name': 'deploy_worker', 'function': None, 'dependencies': ['start_queue']},
                    {'name': 'deploy_ui', 'function': None, 'dependencies': ['deploy_api']}
                ]
            }
        ]
        
        executor = ParallelWaveExecutor()
        
        print(f"Executing {len(waves)} waves with dependency management...")
        result = executor.execute_parallel(waves)
        
        print(f"\n✅ Parallel execution complete!")
        print(f"   Total tasks: {result.total_tasks}")
        print(f"   Completed: {result.completed_tasks}")
        print(f"   Failed: {result.failed_tasks}")
        print(f"   Time: {result.total_time:.2f}s")
        print(f"   Speedup: {result.speedup:.1f}x")
        
        return result
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install networkx")
        return None


def example_5_omega_arbiter():
    """Example 5: Omega Arbiter"""
    print("\n" + "="*70)
    print("Example 5: Omega Arbiter - Enhanced Arbiter with Möbius")
    print("="*70)
    
    try:
        from venom.core.omega_arbiter import OmegaArbiter
        
        # Create test waves
        waves = [
            {
                'id': 'wave-ml',
                'name': 'AI/ML',
                'tasks': [
                    {'name': 'load_model', 'function': None},
                    {'name': 'prepare_data', 'function': None}
                ]
            },
            {
                'id': 'wave-deploy',
                'name': 'Deployment',
                'tasks': [
                    {'name': 'deploy_to_cloud', 'function': None},
                    {'name': 'configure_lb', 'function': None}
                ]
            }
        ]
        
        print(f"Creating Omega Arbiter with Ω-AIOS features enabled...")
        arbiter = OmegaArbiter(enable_omega=True)
        
        print(f"Executing {len(waves)} waves with adaptive throttling...")
        result = arbiter.execute_all_waves_parallel(waves, adaptive_throttle=True)
        
        print(f"\n✅ Omega Arbiter execution complete!")
        print(f"   Waves succeeded: {result['waves_succeeded']}/{result['waves_total']}")
        print(f"   Tasks succeeded: {result['tasks_succeeded']}/{result['tasks_total']}")
        print(f"   Execution time: {result['total_execution_time']:.2f}s")
        
        # Get status
        status = arbiter.get_omega_status()
        if 'theta_metrics' in status:
            print(f"   Current theta: {status['theta_metrics']['theta']:.3f}")
        
        arbiter.stop()
        
        return result
    except ImportError as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main demonstration"""
    print("\n" + "🌌"*35)
    print("VENOM Ω-AIOS - Universal Adaptive AI Operating System")
    print("Complete Demonstration")
    print("🌌"*35 + "\n")
    
    # Run all examples
    profile = example_1_hardware_scan()
    engine = example_2_temporal_compression(profile)
    monitor = example_3_theta_monitoring()
    executor_result = example_4_parallel_execution()
    arbiter_result = example_5_omega_arbiter()
    
    # Summary
    print("\n" + "="*70)
    print("🎉 DEMONSTRATION COMPLETE")
    print("="*70)
    
    success_count = sum([
        profile is not None,
        engine is not None,
        monitor is not None,
        executor_result is not None,
        arbiter_result is not None
    ])
    
    print(f"\n✅ Successfully completed {success_count}/5 examples")
    
    if success_count == 5:
        print("\n🌟 All Ω-AIOS features are working!")
        print("   Your system is ready for universal adaptive execution.")
        print("\n📖 Next steps:")
        print("   - See docs/MOBIUS_ENGINE.md for mathematical details")
        print("   - See docs/UNIVERSAL_DEPLOYMENT.md for deployment guide")
        print("   - Run individual modules for more details:")
        print("     • python venom/hardware/universal_scanner.py")
        print("     • python venom/sync/adaptive_mobius_engine.py")
        print("     • python venom/deployment/parallel_executor.py")
    else:
        print(f"\n⚠️  Some examples failed ({5-success_count}/5)")
        print("   Install missing dependencies: pip install psutil networkx")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
