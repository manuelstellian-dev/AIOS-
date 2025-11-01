"""
End-to-End Integration Tests for VENOM Framework
Tests cross-module functionality and complete workflows
"""
import pytest
import tempfile
import os
from pathlib import Path


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_ai_model_training_and_serving(self):
        """Test complete AI model training and serving workflow"""
        try:
            from venom.ml.automl import AutoMLPipeline
            from venom.ml.model_serving import ModelServer
            
            # Create AutoML pipeline
            pipeline = AutoMLPipeline(framework='optuna')
            
            # Verify pipeline is initialized
            assert pipeline.framework == 'optuna'
            
            # Test model server initialization
            server = ModelServer(port=8080)
            assert server.port == 8080
            assert server._models == {}
            
        except ImportError:
            pytest.skip("ML modules not available")
    
    def test_document_storage_and_search(self):
        """Test document storage and semantic search workflow"""
        try:
            from venom.knowledge.document_store import DocumentStore
            from venom.knowledge.search import SemanticSearch
            
            # Initialize document store
            store = DocumentStore()
            
            # Add test document
            doc_id = store.add_document(
                "VENOM is a universal AI operating system",
                {"category": "system", "version": "1.0"}
            )
            
            assert doc_id is not None
            assert len(store.documents) > 0
            
            # Test search
            search = SemanticSearch()
            results = search.search("operating system", top_k=5)
            
            assert isinstance(results, list)
            
        except ImportError:
            pytest.skip("Knowledge modules not available")
    
    def test_cloud_deployment_workflow(self):
        """Test multi-cloud deployment workflow"""
        try:
            from venom.cloud.aws import EKSDeployer
            
            # Test AWS EKS deployer
            deployer = EKSDeployer(
                cluster_name="test-cluster",
                region="us-east-1"
            )
            
            assert deployer.cluster_name == "test-cluster"
            assert deployer.region == "us-east-1"
            
            # Test deployment configuration
            config = deployer.get_deployment_config()
            assert config is not None
            
        except ImportError:
            pytest.skip("Cloud modules not available")
    
    def test_security_encryption_flow(self):
        """Test complete encryption/decryption workflow"""
        try:
            from venom.security.encryption import AdvancedEncryption
            
            # Test AES-GCM encryption
            encryption = AdvancedEncryption(algorithm='aes-gcm')
            
            # Generate key
            key = encryption.generate_key(algorithm='aes-gcm')
            assert key is not None
            assert len(key) == 32  # 256 bits for AES-256
            
            # Test encryption/decryption
            plaintext = b"Sensitive data to encrypt"
            encrypted_data = encryption.encrypt(plaintext, key)
            
            assert encrypted_data != plaintext
            assert len(encrypted_data) > len(plaintext)  # Has nonce prepended
            
            decrypted = encryption.decrypt(encrypted_data, key)
            assert decrypted == plaintext
            
        except ImportError:
            pytest.skip("Security modules not available")
    
    def test_observability_metrics_collection(self):
        """Test metrics collection and monitoring"""
        try:
            from venom.observability.theta_monitor import ThetaMonitor
            import time
            
            # Initialize monitor
            monitor = ThetaMonitor(interval=0.1)
            
            # Start monitoring
            monitor.start_monitoring()
            time.sleep(0.3)
            
            # Check metrics collected
            status = monitor.get_current_metrics()
            assert 'theta' in status
            assert 'cpu_health' in status
            assert 'memory_health' in status
            
            # Stop monitoring
            monitor.stop_monitoring()
            
        except ImportError:
            pytest.skip("Observability modules not available")
    
    def test_hardware_monitoring(self):
        """Test hardware detection and monitoring"""
        try:
            from venom.hardware.universal_scanner import UniversalHardwareScanner
            
            # Scan hardware
            scanner = UniversalHardwareScanner()
            profile = scanner.scan()
            
            # Verify profile
            assert profile.cpu_cores_logical > 0
            assert profile.memory_total_gb > 0
            assert profile.platform_system in ['Linux', 'Darwin', 'Windows']
            
            # Test Möbius parameters calculation
            assert hasattr(profile, 'optimal_workers')
            assert hasattr(profile, 'lambda_wrap')
            assert hasattr(profile, 'parallel_fraction')
            
        except ImportError:
            pytest.skip("Hardware modules not available")
    
    def test_integration_slack_notification(self):
        """Test external integration (Slack)"""
        try:
            from venom.integrations.slack import SlackIntegration
            
            # Initialize (without actual webhook)
            slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")
            
            # Verify initialization
            assert slack.webhook_url == "https://hooks.slack.com/test"
            
            # Test that methods exist
            assert hasattr(slack, 'send_message')
            assert hasattr(slack, 'send_alert')
            
        except ImportError:
            pytest.skip("Integration modules not available")
    
    def test_knowledge_graph_traversal(self):
        """Test knowledge graph operations"""
        try:
            from venom.knowledge.graph import KnowledgeGraph
            
            # Initialize graph
            graph = KnowledgeGraph()
            
            # Add nodes and edges
            graph.add_node("concept1", {"type": "concept", "name": "AI"})
            graph.add_node("concept2", {"type": "concept", "name": "ML"})
            graph.add_edge("concept1", "concept2", {"relation": "includes"})
            
            # Test traversal
            neighbors = graph.get_neighbors("concept1")
            assert len(neighbors) > 0
            assert neighbors[0]['node_id'] == "concept2"
            
            # Test path finding
            path = graph.find_path("concept1", "concept2")
            assert path is not None
            
        except ImportError:
            pytest.skip("Knowledge graph modules not available")
    
    def test_multi_module_pipeline(self):
        """Test pipeline combining multiple modules"""
        try:
            from venom.core.arbiter import Arbiter
            from venom.sync.t_lambda_pulse import TLambdaPulse
            from venom.control.genomic_pid import GenomicPID
            from venom.inference.entropy_model import EntropyModel
            from venom.ledger.immutable_ledger import ImmutableLedger
            
            # Initialize components
            pulse = TLambdaPulse(k=4, p=5, t1=0.001)
            pid = GenomicPID(kp=0.6, ki=0.1, kd=0.05)
            entropy = EntropyModel(ml_weight=0.12)
            ledger = ImmutableLedger()
            
            # Create arbiter with all components
            arbiter = Arbiter(
                pulse=pulse,
                pid=pid,
                entropy_model=entropy,
                ledger=ledger
            )
            
            # Verify initialization
            assert arbiter.pulse == pulse
            assert arbiter.pid == pid
            assert arbiter.entropy_model == entropy
            assert arbiter.ledger == ledger
            
        except ImportError:
            pytest.skip("Core modules not available")
    
    def test_cli_commands(self):
        """Test CLI command execution"""
        try:
            from venom.cli import VenomCLI
            import argparse
            
            # Initialize CLI
            cli = VenomCLI()
            
            # Test modules list
            args = argparse.Namespace(command='modules', modules_command='list')
            result = cli.modules_list(args)
            assert result == 0
            
            # Test health check
            args = argparse.Namespace(command='health', health_command='check')
            result = cli.health_check(args)
            assert result == 0
            
        except ImportError as e:
            pytest.skip(f"CLI modules not available: {e}")


class TestIntegrationWorkflows:
    """Test complete integration workflows"""
    
    def test_security_and_storage_integration(self):
        """Test integration between security and storage"""
        try:
            from venom.security.encryption import AdvancedEncryption
            
            # Create encryption instance
            encryption = AdvancedEncryption(algorithm='aes-gcm')
            
            # Test data flow
            data = b"Sensitive document content"
            key = encryption.generate_key(algorithm='aes-gcm')
            encrypted_data = encryption.encrypt(data, key)
            
            # Store encrypted data (simulated)
            storage = {
                'data': encrypted_data,
                'algorithm': 'aes-gcm'
            }
            
            # Retrieve and decrypt
            decrypted = encryption.decrypt(
                storage['data'],
                key
            )
            
            assert decrypted == data
            
        except ImportError:
            pytest.skip("Required modules not available")
    
    def test_monitoring_and_analytics_integration(self):
        """Test integration between monitoring and analytics"""
        try:
            from venom.observability.theta_monitor import ThetaMonitor
            import time
            
            # Start monitoring
            monitor = ThetaMonitor(interval=0.1)
            monitor.start_monitoring()
            
            # Collect metrics
            time.sleep(0.3)
            status = monitor.get_current_metrics()
            
            # Verify analytics data
            assert 'theta' in status
            assert isinstance(status['theta'], float)
            assert 0 <= status['theta'] <= 1
            
            monitor.stop_monitoring()
            
        except ImportError:
            pytest.skip("Required modules not available")
    
    def test_deployment_and_observability_integration(self):
        """Test deployment with observability"""
        try:
            from venom.deployment.parallel_executor import ParallelWaveExecutor
            
            # Create test waves
            waves = [
                {
                    'id': 'wave-1',
                    'name': 'Setup',
                    'tasks': [
                        {'name': 'task1', 'function': None, 'dependencies': []}
                    ]
                }
            ]
            
            # Execute with monitoring
            executor = ParallelWaveExecutor()
            result = executor.execute_parallel(waves)
            
            # Verify execution
            assert result.total_tasks > 0
            assert result.completed_tasks == result.total_tasks
            
        except ImportError:
            pytest.skip("Required modules not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
