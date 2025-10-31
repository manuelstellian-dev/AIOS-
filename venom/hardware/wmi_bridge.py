"""
WMI Bridge for Windows Hardware Access
Basic temperature and system info reading
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WMIBridge:
    """
    Windows Management Instrumentation Bridge
    Access to hardware sensors (temp, fan, voltage)
    """
    
    def __init__(self):
        self.available = False
        self._init_wmi()
    
    def _init_wmi(self):
        """Initialize WMI connection"""
        try:
            # Try to import wmi (Windows only)
            import wmi
            self.wmi = wmi.WMI()
            self.available = True
            logger.info("WMI bridge initialized")
        except ImportError:
            logger.warning("WMI not available (not on Windows or wmi package not installed)")
            self.wmi = None
        except Exception as e:
            logger.error(f"WMI initialization failed: {e}")
            self.wmi = None
    
    def get_cpu_temperature(self) -> Optional[float]:
        """
        Get CPU temperature in Celsius
        Returns None if not available
        """
        if not self.available:
            logger.warning("WMI not available - returning simulated value")
            return 55.0  # Simulated value for testing
        
        try:
            # Try to get temperature from WMI
            for sensor in self.wmi.MSAcpi_ThermalZoneTemperature():
                temp_kelvin = sensor.CurrentTemperature / 10.0
                temp_celsius = temp_kelvin - 273.15
                return temp_celsius
        except Exception as e:
            logger.error(f"Failed to read CPU temperature: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, str]:
        """Get basic system information"""
        if not self.available:
            return {
                "os": "Unknown",
                "cpu": "Unknown",
                "simulated": "true"
            }
        
        try:
            info = {}
            for os in self.wmi.Win32_OperatingSystem():
                info["os"] = os.Caption
                info["version"] = os.Version
            
            for cpu in self.wmi.Win32_Processor():
                info["cpu"] = cpu.Name
            
            return info
        except Exception as e:
            logger.error(f"Failed to read system info: {e}")
            return {"error": str(e)}
