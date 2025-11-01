#!/usr/bin/env python3
"""
VENOM Ω-AIOS Command Line Interface

Commands:
- scan: Display hardware profile
- run: Execute with Möbius compression
- benchmark: Performance benchmark
- monitor: Real-time theta monitoring
- config: Show configuration
"""

import sys
import time
import argparse
from typing import Optional


def cmd_scan():
    """Scan and display hardware profile"""
    try:
        from venom.hardware.universal_scanner import UniversalHardwareScanner
        
        print("🔍 Scanning hardware...")
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        scanner.print_profile()
        
        return 0
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil")
        return 1
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        return 1


def cmd_compress(sequential_hours: float):
    """Show temporal compression estimate"""
    try:
        from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine
        
        print(f"⚡ Calculating temporal compression for {sequential_hours}h...")
        
        engine = AdaptiveMobiusEngine(auto_detect=True)
        result = engine.compress_time(sequential_hours)
        engine.print_compression_summary(result)
        
        return 0
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil")
        return 1
    except Exception as e:
        print(f"❌ Compression calculation failed: {e}")
        return 1


def cmd_benchmark():
    """Run performance benchmark"""
    try:
        from venom.deployment.parallel_executor import ParallelWaveExecutor
        
        print("⚡ Running VENOM Ω-AIOS Benchmark...")
        print("=" * 60)
        
        # Create test waves
        waves = []
        for wave_id in range(1, 6):
            tasks = []
            for task_id in range(5):
                tasks.append({
                    'name': f'task_{wave_id}_{task_id}',
                    'function': None,
                    'dependencies': []
                })
            
            waves.append({
                'id': f'wave-{wave_id}',
                'name': f'Wave {wave_id}',
                'tasks': tasks
            })
        
        # Execute
        executor = ParallelWaveExecutor()
        result = executor.execute_parallel(waves)
        
        # Print results
        print("\n📊 Benchmark Results:")
        print("=" * 60)
        print(f"Total Tasks:     {result.total_tasks}")
        print(f"Completed:       {result.completed_tasks}")
        print(f"Failed:          {result.failed_tasks}")
        print(f"Execution Time:  {result.total_time:.2f}s")
        print(f"Speedup:         {result.speedup:.1f}x")
        print(f"Tasks/Second:    {result.completed_tasks / result.total_time:.1f}")
        print("=" * 60)
        
        return 0
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil networkx")
        return 1
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1


def cmd_monitor(duration: int = 10):
    """Monitor system theta in real-time"""
    try:
        from venom.observability.theta_monitor import ThetaMonitor
        
        print(f"📊 Starting Theta Monitor for {duration}s...")
        print("Press Ctrl+C to stop")
        print()
        
        monitor = ThetaMonitor(interval=1.0)
        monitor.start_monitoring()
        
        try:
            for i in range(duration):
                time.sleep(1)
                if i % 2 == 0:
                    monitor.print_status()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            monitor.stop_monitoring()
        
        print("\n✅ Monitoring complete")
        return 0
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil")
        return 1
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return 1


def cmd_config():
    """Display configuration"""
    try:
        from venom.sync.adaptive_mobius_engine import AdaptiveMobiusEngine
        from venom.hardware.universal_scanner import UniversalHardwareScanner
        
        print("⚙️  VENOM Ω-AIOS Configuration")
        print("=" * 60)
        
        # Get hardware profile
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        # Get Möbius config
        engine = AdaptiveMobiusEngine(auto_detect=True)
        
        print("\n🖥️  Hardware:")
        print(f"  Platform:     {profile.platform_system} {profile.platform_machine}")
        print(f"  CPU Cores:    {profile.cpu_cores_logical} ({profile.cpu_vendor})")
        print(f"  Memory:       {profile.memory_total_gb:.1f} GB")
        print(f"  GPU:          ", end="")
        if profile.has_cuda:
            print("CUDA", end="")
        elif profile.has_rocm:
            print("ROCm", end="")
        elif profile.has_metal:
            print("Metal", end="")
        else:
            print("None", end="")
        print()
        
        print("\n📐 Möbius Engine:")
        print(f"  Workers (N):        {engine.config.get('n_cores', 'N/A')}")
        print(f"  Lambda Wrap (Λ):    {engine.config.get('lambda_wrap', 'N/A'):.1f}")
        print(f"  Parallel Frac (P):  {engine.config.get('parallel_fraction', 'N/A'):.3f}")
        
        theta = engine.calculate_theta()
        mode = engine.get_mode_name(theta)
        print(f"  Current Theta (θ):  {theta:.3f} [{mode}]")
        
        print("\n🚀 Estimated Performance:")
        speedup = engine.total_speedup(theta)
        print(f"  Total Speedup:      {speedup:.1f}x")
        print(f"  840h → {840/speedup:.2f}h")
        
        print("=" * 60)
        
        return 0
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install dependencies: pip install psutil")
        return 1
    except Exception as e:
        print(f"❌ Configuration display failed: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='VENOM Ω-AIOS Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  venom-omega scan                    # Scan hardware
  venom-omega compress 840            # Calculate compression for 840h
  venom-omega benchmark               # Run benchmark
  venom-omega monitor 30              # Monitor for 30s
  venom-omega config                  # Show configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    subparsers.add_parser('scan', help='Scan and display hardware profile')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Calculate temporal compression')
    compress_parser.add_argument('hours', type=float, help='Sequential time in hours')
    
    # Benchmark command
    subparsers.add_parser('benchmark', help='Run performance benchmark')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system theta')
    monitor_parser.add_argument('--duration', type=int, default=10, help='Duration in seconds')
    
    # Config command
    subparsers.add_parser('config', help='Display configuration')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'scan':
        return cmd_scan()
    elif args.command == 'compress':
        return cmd_compress(args.hours)
    elif args.command == 'benchmark':
        return cmd_benchmark()
    elif args.command == 'monitor':
        return cmd_monitor(args.duration)
    elif args.command == 'config':
        return cmd_config()
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
