"""Test Production Hardening"""
import pytest
from venom.ops.production_hardening import (
    ProductionValidator,
    ValidationStatus,
    SeverityLevel
)

def test_production_validator_init():
    """Test ProductionValidator initialization"""
    validator = ProductionValidator()
    
    assert len(validator.validation_results) == 0
    assert len(validator.vulnerabilities) == 0

def test_validate_security():
    """Test security validation"""
    validator = ProductionValidator()
    
    report = validator.validate_security(scan_cves=True, check_secrets=True)
    
    assert report["category"] == "security"
    assert report["total_checks"] > 0
    assert "passed" in report
    assert "failed" in report
    assert "warnings" in report
    assert "overall_status" in report
    assert report["vulnerabilities_found"] >= 0
    assert report["critical_issues"] >= 0
    assert len(report["checks"]) > 0
    
    # Verify validation results were stored
    assert len(validator.validation_results) > 0
    
    # Check that specific security checks were performed
    check_names = [check["name"] for check in report["checks"]]
    assert "cve_scan" in check_names
    assert "secrets_check" in check_names

def test_validate_performance():
    """Test performance validation"""
    validator = ProductionValidator()
    
    # Test with default targets
    report = validator.validate_performance(
        target_latency_ms=100.0,
        target_throughput=1000.0
    )
    
    assert report["category"] == "performance"
    assert report["total_checks"] > 0
    assert "metrics" in report
    assert "latency_ms" in report["metrics"]
    assert "throughput_rps" in report["metrics"]
    assert report["overall_status"] in ["PASS", "FAIL"]
    
    # Verify latency is under target
    assert report["metrics"]["latency_ms"] < 100.0
    
    # Verify throughput exceeds target
    assert report["metrics"]["throughput_rps"] > 1000.0
    
    # Check that specific performance checks were performed
    check_names = [check["name"] for check in report["checks"]]
    assert "latency_check" in check_names
    assert "throughput_check" in check_names

def test_validate_reliability():
    """Test reliability validation"""
    validator = ProductionValidator()
    
    report = validator.validate_reliability(
        target_uptime=99.9,
        target_error_rate=0.1
    )
    
    assert report["category"] == "reliability"
    assert report["total_checks"] > 0
    assert "metrics" in report
    assert "uptime_percent" in report["metrics"]
    assert "error_rate_percent" in report["metrics"]
    assert report["overall_status"] in ["PASS", "FAIL"]
    
    # Verify uptime exceeds target
    assert report["metrics"]["uptime_percent"] >= 99.9
    
    # Verify error rate is under target
    assert report["metrics"]["error_rate_percent"] < 0.1
    
    # Check that specific reliability checks were performed
    check_names = [check["name"] for check in report["checks"]]
    assert "uptime_check" in check_names
    assert "error_rate_check" in check_names

def test_validate_observability():
    """Test observability validation"""
    validator = ProductionValidator()
    
    report = validator.validate_observability()
    
    assert report["category"] == "observability"
    assert report["total_checks"] > 0
    assert "passed" in report
    assert "failed" in report
    assert "warnings" in report
    assert report["overall_status"] in ["PASS", "FAIL"]
    assert len(report["checks"]) > 0
    
    # Check that observability checks cover metrics, logs, and traces
    check_names = [check["name"] for check in report["checks"]]
    assert "metrics_collection" in check_names
    assert "log_aggregation" in check_names
    assert "distributed_tracing" in check_names

def test_generate_readiness_report():
    """Test generating comprehensive production readiness report"""
    validator = ProductionValidator()
    
    report = validator.generate_readiness_report()
    
    # Verify report structure
    assert "timestamp" in report
    assert "overall_status" in report
    assert report["overall_status"] in ["READY", "NOT_READY"]
    
    # Verify summary
    assert "summary" in report
    summary = report["summary"]
    assert "total_checks" in summary
    assert "passed" in summary
    assert "failed" in summary
    assert "success_rate" in summary
    
    # Verify all categories are present
    assert "categories" in report
    categories = report["categories"]
    assert "security" in categories
    assert "performance" in categories
    assert "reliability" in categories
    assert "observability" in categories
    
    # Verify recommendations
    assert "recommendations" in report
    assert len(report["recommendations"]) > 0
    
    # Verify deployment readiness
    assert "deployment_readiness" in report
    assert "can_deploy" in report["deployment_readiness"]
    assert "blocking_issues" in report["deployment_readiness"]
    
    # Since all simulated checks pass, system should be ready
    assert report["overall_status"] == "READY"
    assert report["deployment_readiness"]["can_deploy"] is True
    assert summary["success_rate"] >= 90.0  # High success rate expected
