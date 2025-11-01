"""Tests for UniversalHardwareScanner"""

import pytest
from venom.hardware.universal_scanner import (
    UniversalHardwareScanner,
    HardwareProfile,
    scan_hardware
)


class TestUniversalHardwareScanner:
    """Test suite for UniversalHardwareScanner"""
    
    def test_scanner_initialization(self):
        """Test scanner can be initialized"""
        scanner = UniversalHardwareScanner()
        assert scanner is not None
    
    def test_scan_returns_profile(self):
        """Test scan returns HardwareProfile"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        assert isinstance(profile, HardwareProfile)
    
    def test_profile_has_cpu_info(self):
        """Test profile contains CPU information"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.cpu_cores_physical > 0
        assert profile.cpu_cores_logical > 0
        assert profile.cpu_cores_logical >= profile.cpu_cores_physical
        assert profile.cpu_arch != ""
    
    def test_profile_has_memory_info(self):
        """Test profile contains memory information"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.memory_total_gb > 0
        assert profile.memory_available_gb >= 0
        assert profile.memory_usage_percent >= 0
        assert profile.memory_usage_percent <= 100
    
    def test_profile_has_platform_info(self):
        """Test profile contains platform information"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.platform_system != ""
        assert profile.platform_machine != ""
    
    def test_optimal_workers_calculation(self):
        """Test optimal workers calculation"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.optimal_workers > 0
        assert profile.optimal_workers <= 64
    
    def test_lambda_wrap_in_range(self):
        """Test lambda_wrap is within valid range"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.lambda_wrap >= scanner.LAMBDA_WRAP_MIN
        assert profile.lambda_wrap <= scanner.LAMBDA_WRAP_MAX
    
    def test_parallel_fraction_in_range(self):
        """Test parallel_fraction is within valid range"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert profile.parallel_fraction >= 0.6
        assert profile.parallel_fraction <= 0.95
    
    def test_to_dict_export(self):
        """Test profile can be exported to dict"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        profile_dict = scanner.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert 'cpu_cores_logical' in profile_dict
        assert 'memory_total_gb' in profile_dict
        assert 'optimal_workers' in profile_dict
    
    def test_print_profile_no_error(self):
        """Test print_profile doesn't raise errors"""
        scanner = UniversalHardwareScanner()
        scanner.scan()
        
        # Should not raise any exceptions
        scanner.print_profile()
    
    def test_scan_hardware_convenience_function(self):
        """Test scan_hardware convenience function"""
        profile = scan_hardware()
        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_cores_logical > 0
    
    def test_gpu_detection(self):
        """Test GPU detection returns boolean flags"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert isinstance(profile.has_cuda, bool)
        assert isinstance(profile.has_rocm, bool)
        assert isinstance(profile.has_metal, bool)
        assert isinstance(profile.has_opencl, bool)
    
    def test_capabilities_detection(self):
        """Test system capabilities detection"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        assert isinstance(profile.has_hyperthreading, bool)
        assert isinstance(profile.has_virtualization, bool)
        assert isinstance(profile.is_docker, bool)
        assert isinstance(profile.is_kubernetes, bool)
    
    def test_cpu_vendor_detection(self):
        """Test CPU vendor detection"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        # Vendor should be one of known types or unknown
        valid_vendors = ['Intel', 'AMD', 'ARM', 'x86', 'unknown']
        assert profile.cpu_vendor in valid_vendors
    
    def test_thermal_health_optional(self):
        """Test thermal data is optional"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        # Temperature may be None if sensors not available
        assert profile.cpu_temperature is None or profile.cpu_temperature > 0
    
    def test_multiple_scans_consistent(self):
        """Test multiple scans return consistent results"""
        scanner = UniversalHardwareScanner()
        profile1 = scanner.scan()
        profile2 = scanner.scan()
        
        # Core counts should be the same
        assert profile1.cpu_cores_physical == profile2.cpu_cores_physical
        assert profile1.cpu_cores_logical == profile2.cpu_cores_logical
        
        # Architecture should be the same
        assert profile1.cpu_arch == profile2.cpu_arch
        assert profile1.platform_system == profile2.platform_system
    
    def test_scanner_handles_errors_gracefully(self):
        """Test scanner handles errors gracefully"""
        scanner = UniversalHardwareScanner()
        
        # Even if some sensors fail, scan should complete
        profile = scanner.scan()
        assert profile is not None
        assert profile.cpu_cores_logical > 0
    
    def test_adaptive_parameters_reasonable(self):
        """Test adaptive parameters are reasonable"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        # Workers should be proportional to cores
        assert profile.optimal_workers <= profile.cpu_cores_logical * 2
        
        # Lambda should scale with compute capacity
        min_expected = profile.cpu_cores_logical * 25  # At least half of base
        assert profile.lambda_wrap >= min_expected or profile.lambda_wrap == scanner.LAMBDA_WRAP_MIN
    
    def test_low_memory_reduces_workers(self):
        """Test that low memory scenarios are handled"""
        scanner = UniversalHardwareScanner()
        profile = scanner.scan()
        
        # If system has very low memory, workers should be reduced
        if profile.memory_total_gb < 2:
            assert profile.optimal_workers <= 2
