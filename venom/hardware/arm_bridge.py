"""
ARM Bridge for ARM CPU and Raspberry Pi Hardware Access
Provides ARM CPU optimization and GPIO control for Raspberry Pi
"""

import logging
import platform
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ARMBridge:
    """
    ARM Bridge for ARM CPUs and Raspberry Pi
    Provides NEON optimization, temperature monitoring, and GPIO control
    Gracefully falls back to simulated values if ARM hardware is unavailable
    """
    
    def __init__(self):
        """Initialize ARM bridge"""
        self.available = False
        self.is_raspberry_pi = False
        self.gpio_available = False
        self.gpio = None
        self._init_arm()
    
    def _init_arm(self):
        """Initialize ARM connection"""
        try:
            # Check if running on ARM architecture
            machine = platform.machine().lower()
            self.available = machine in ['aarch64', 'armv7l', 'armv8l', 'arm64']
            
            if self.available:
                logger.info(f"ARM bridge initialized successfully on {machine}")
                
                # Try to detect Raspberry Pi
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        self.is_raspberry_pi = 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
                except:
                    pass
                
                # Try to initialize GPIO (Raspberry Pi only)
                if self.is_raspberry_pi:
                    try:
                        import RPi.GPIO as GPIO
                        self.gpio = GPIO
                        self.gpio_available = True
                        logger.info("Raspberry Pi GPIO initialized")
                    except ImportError:
                        logger.warning("RPi.GPIO not installed - GPIO functions unavailable")
                    except Exception as e:
                        logger.warning(f"GPIO initialization failed: {e}")
            else:
                logger.warning("Not running on ARM - using simulated values")
        except Exception as e:
            logger.error(f"ARM initialization failed: {e}")
    
    def is_available(self) -> bool:
        """
        Check if ARM hardware is available
        Returns True if running on ARM architecture
        """
        return self.available
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Get ARM CPU information
        
        Returns:
            Dict with model, cores, frequency, features
        """
        if not self.available:
            return {
                "model": "Simulated ARM Cortex-A72",
                "cores": 4,
                "max_frequency_mhz": 1800,
                "architecture": "armv8",
                "features": ["neon", "vfpv4"],
                "simulated": True
            }
        
        try:
            import psutil
            
            cpu_info = {
                "model": "ARM CPU",
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "architecture": platform.machine(),
                "is_raspberry_pi": self.is_raspberry_pi,
                "simulated": False
            }
            
            # Try to get CPU model from /proc/cpuinfo
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line.lower() or 'hardware' in line.lower():
                            cpu_info['model'] = line.split(':')[1].strip()
                            break
            except:
                pass
            
            # Try to get CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info['current_frequency_mhz'] = freq.current
                    cpu_info['max_frequency_mhz'] = freq.max
            except:
                pass
            
            # Try to detect NEON support
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    features = []
                    if 'neon' in cpuinfo.lower():
                        features.append('neon')
                    if 'vfp' in cpuinfo.lower():
                        features.append('vfp')
                    if features:
                        cpu_info['features'] = features
            except:
                pass
            
            return cpu_info
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {}
    
    def optimize_neon(self) -> bool:
        """
        Check if NEON SIMD optimization is available
        
        Returns:
            True if NEON is supported
        """
        if not self.available:
            logger.debug("ARM not available - simulating NEON check")
            return True  # Simulated
        
        try:
            # Check for NEON support in /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'neon' in cpuinfo.lower()
        except Exception as e:
            logger.error(f"Failed to check NEON support: {e}")
            return False
    
    def get_temperature(self) -> float:
        """
        Get CPU temperature in Celsius
        
        Returns:
            Temperature in Celsius or -1.0 if unavailable
        """
        if not self.available:
            logger.debug("ARM not available - simulating temperature")
            return 45.5  # Simulated temperature
        
        try:
            # Try multiple temperature sources
            temp_sources = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/thermal/thermal_zone1/temp',
            ]
            
            for source in temp_sources:
                try:
                    with open(source, 'r') as f:
                        temp = float(f.read().strip()) / 1000.0  # Convert from millidegrees
                        return temp
                except:
                    continue
            
            # Alternative: try psutil sensors_temperatures
            try:
                import psutil
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
            except:
                pass
            
            logger.warning("Temperature sensor not found")
            return -1.0
        except Exception as e:
            logger.error(f"Failed to get temperature: {e}")
            return -1.0
    
    def set_governor(self, mode: str = 'performance'):
        """
        Set CPU governor mode
        
        Args:
            mode: Governor mode ('performance', 'powersave', 'ondemand')
        """
        if not self.available:
            logger.debug(f"ARM not available - simulating governor set to {mode}")
            return
        
        valid_modes = ['performance', 'powersave', 'ondemand', 'conservative', 'schedutil']
        if mode not in valid_modes:
            logger.error(f"Invalid governor mode: {mode}. Valid modes: {valid_modes}")
            return
        
        try:
            import subprocess
            import os
            
            # Get number of CPUs
            import psutil
            cpu_count = psutil.cpu_count()
            
            # Try to set governor for each CPU
            for cpu in range(cpu_count):
                governor_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                try:
                    # This requires root permissions
                    if os.path.exists(governor_path):
                        subprocess.run(
                            ['sudo', 'bash', '-c', f'echo {mode} > {governor_path}'],
                            check=True,
                            timeout=1
                        )
                except subprocess.CalledProcessError:
                    logger.warning(f"Failed to set governor for CPU {cpu} (may require root)")
                except:
                    pass
            
            logger.info(f"CPU governor set to {mode} (if permissions allow)")
        except Exception as e:
            logger.error(f"Failed to set governor: {e}")
    
    # GPIO functions (Raspberry Pi only)
    
    def gpio_setup(self, pin: int, mode: str):
        """
        Setup GPIO pin
        
        Args:
            pin: GPIO pin number (BCM numbering)
            mode: Pin mode ('IN' or 'OUT')
        """
        if not self.gpio_available:
            logger.debug(f"GPIO not available - simulating pin {pin} setup as {mode}")
            return
        
        try:
            if mode.upper() == 'IN':
                self.gpio.setup(pin, self.gpio.IN)
            elif mode.upper() == 'OUT':
                self.gpio.setup(pin, self.gpio.OUT)
            else:
                logger.error(f"Invalid GPIO mode: {mode}. Use 'IN' or 'OUT'")
        except Exception as e:
            logger.error(f"GPIO setup failed: {e}")
    
    def gpio_read(self, pin: int) -> int:
        """
        Read GPIO pin value
        
        Args:
            pin: GPIO pin number (BCM numbering)
            
        Returns:
            Pin value (0 or 1), or -1 if unavailable
        """
        if not self.gpio_available:
            logger.debug(f"GPIO not available - simulating read from pin {pin}")
            return 0  # Simulated
        
        try:
            return self.gpio.input(pin)
        except Exception as e:
            logger.error(f"GPIO read failed: {e}")
            return -1
    
    def gpio_write(self, pin: int, value: int):
        """
        Write GPIO pin value
        
        Args:
            pin: GPIO pin number (BCM numbering)
            value: Pin value (0 or 1)
        """
        if not self.gpio_available:
            logger.debug(f"GPIO not available - simulating write {value} to pin {pin}")
            return
        
        try:
            if value not in [0, 1]:
                logger.error(f"Invalid GPIO value: {value}. Use 0 or 1")
                return
            self.gpio.output(pin, value)
        except Exception as e:
            logger.error(f"GPIO write failed: {e}")
    
    def gpio_cleanup(self):
        """Cleanup GPIO resources"""
        if not self.gpio_available:
            logger.debug("GPIO not available - simulating cleanup")
            return
        
        try:
            self.gpio.cleanup()
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"GPIO cleanup failed: {e}")
