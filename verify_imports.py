#!/usr/bin/env python3
"""
Verify Imports - Test all critical module imports before running full test suite
This helps identify import issues early without running full tests
"""
import sys
import traceback
from typing import List, Tuple

# Critical modules to test (in order of dependency)
MODULES_TO_TEST = [
    # Core modules (no heavy ML dependencies)
    "venom.core.constants",
    "venom.sync.pulse",
    "venom.control.genomic_pid",
    
    # Flows (no heavy dependencies)
    "venom.flows.parallel_flows",
    
    # Security modules
    "venom.security.encryption",
    "venom.security.signing",
    "venom.security.auth",
    "venom.security.mfa",
    "venom.security.secrets",
    
    # Ledger
    "venom.ledger.immutable_ledger",
    
    # Mesh
    "venom.mesh.p2p",
    "venom.mesh.rate_limiter",
    
    # Observability
    "venom.observability.metrics",
    "venom.observability.health",
    "venom.observability.monitoring",
    "venom.observability.tracing",
    "venom.observability.theta_monitor",
    
    # Operations
    "venom.ops.backup",
    "venom.ops.audit",
    "venom.ops.shutdown",
    "venom.ops.production_hardening",
    
    # Integrations
    "venom.integrations.database",
    "venom.integrations.email",
    "venom.integrations.slack",
    "venom.integrations.webhook",
    
    # Deployment
    "venom.deployment.parallel_executor",
    "venom.deployment.edge_deploy",
    "venom.deployment.k8s_autoscale",
    "venom.deployment.multi_region",
    
    # Benchmark
    "venom.benchmark.performance",
    
    # Testing
    "venom.testing.chaos_engineering",
    "venom.testing.load_test",
    
    # ML/Inference (requires torch) - test separately
    "venom.inference.entropy_model",
    
    # Core Arbiter (requires entropy_model)
    "venom.core.arbiter",
    "venom.core.omega_arbiter",
    
    # Analytics (some require sklearn/numpy)
    "venom.analytics.time_series",
    "venom.analytics.stream_processor",
    "venom.analytics.streaming",
    "venom.analytics.anomaly_detector",
    "venom.analytics.predictor",
    "venom.analytics.predictive",
    
    # Knowledge (some require torch/transformers)
    "venom.knowledge.graph",
    "venom.knowledge.search",
    "venom.knowledge.document_store",
    
    # ML modules (require torch/transformers/optuna)
    "venom.ml.registry",
    "venom.ml.automl",
    "venom.ml.model_serving",
    "venom.ml.transformer_bridge",
    "venom.ml.vision_models",
    
    # Hardware bridges (may require platform-specific libs)
    "venom.hardware.universal_scanner",
    "venom.hardware.cuda_bridge",
    "venom.hardware.rocm_bridge",
    "venom.hardware.metal_bridge",
    "venom.hardware.oneapi_bridge",
    "venom.hardware.tpu_bridge",
    "venom.hardware.arm_bridge",
    "venom.hardware.wmi_bridge",
    
    # Cloud modules (require cloud SDKs - optional)
    "venom.cloud.aws.s3_backup",
    "venom.cloud.aws.lambda_handler",
    "venom.cloud.aws.eks_deployer",
    "venom.cloud.azure.blob_backup",
    "venom.cloud.azure.functions",
    "venom.cloud.azure.aks_deployer",
    "venom.cloud.gcp.storage_backup",
    "venom.cloud.gcp.cloud_functions",
    "venom.cloud.gcp.gke_deployer",
    
    # CLI
    "venom.cli.main",
    "venom.cli.omega_cli",
    "venom.cli.dashboard",
    
    # FEV concepts
    "venom.fev.concepts",
    
    # Main package
    "venom",
]


def test_import(module_name: str) -> Tuple[bool, str]:
    """
    Test if a module can be imported
    
    Args:
        module_name: Full module path to test
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        __import__(module_name)
        return True, ""
    except ModuleNotFoundError as e:
        # Check if it's a missing optional dependency
        missing_dep = str(e).split("'")[1] if "'" in str(e) else str(e)
        return False, f"Missing dependency: {missing_dep}"
    except ImportError as e:
        return False, f"Import error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {type(e).__name__}: {str(e)}"


def main():
    """Run import verification for all modules"""
    print("=" * 80)
    print("VENOM Import Verification")
    print("=" * 80)
    print()
    
    failed: List[Tuple[str, str]] = []
    succeeded: List[str] = []
    skipped: List[Tuple[str, str]] = []
    
    for i, module in enumerate(MODULES_TO_TEST, 1):
        sys.stdout.write(f"[{i:3d}/{len(MODULES_TO_TEST)}] Testing {module:50s} ... ")
        sys.stdout.flush()
        
        success, error = test_import(module)
        
        if success:
            print("✅ OK")
            succeeded.append(module)
        elif "Missing dependency" in error and any(dep in error for dep in [
            "boto3", "azure", "google", "transformers", "optuna",
            "RPi.GPIO", "win32", "wmi"
        ]):
            # Optional dependency - expected to be missing
            print(f"⚠️  SKIP ({error.split(':')[1].strip()})")
            skipped.append((module, error))
        else:
            print(f"❌ FAIL")
            print(f"    Error: {error}")
            failed.append((module, error))
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✅ Succeeded: {len(succeeded)}/{len(MODULES_TO_TEST)}")
    print(f"⚠️  Skipped (optional deps): {len(skipped)}/{len(MODULES_TO_TEST)}")
    print(f"❌ Failed: {len(failed)}/{len(MODULES_TO_TEST)}")
    print()
    
    if skipped:
        print("Skipped modules (optional dependencies):")
        for module, error in skipped:
            print(f"  - {module}: {error}")
        print()
    
    if failed:
        print("❌ FAILED MODULES:")
        for module, error in failed:
            print(f"  - {module}")
            print(f"    {error}")
        print()
        print("❌ Import verification FAILED!")
        print(f"   {len(failed)} critical module(s) failed to import")
        return 1
    else:
        print("✅ All critical imports successful!")
        print(f"   {len(succeeded)} modules imported successfully")
        if skipped:
            print(f"   {len(skipped)} modules skipped (optional dependencies)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
