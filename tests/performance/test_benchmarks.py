"""
Performance Benchmark Tests for VENOM Framework
Tests performance characteristics and optimization
"""
import pytest
import time
from typing import List, Dict, Any


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    def test_document_store_performance(self):
        """Benchmark document storage operations"""
        try:
            from venom.knowledge.document_store import DocumentStore
            
            store = DocumentStore()
            
            # Benchmark document addition
            num_docs = 100
            start_time = time.time()
            
            for i in range(num_docs):
                doc_id = store.add_document(
                    f"Document content {i}",
                    {"index": i, "category": "test"}
                )
                assert doc_id is not None
            
            elapsed_time = time.time() - start_time
            docs_per_second = num_docs / elapsed_time
            
            # Performance assertion: should handle at least 50 docs/second
            assert docs_per_second > 50, f"Too slow: {docs_per_second:.1f} docs/s"
            
            # Benchmark document retrieval
            start_time = time.time()
            
            for i in range(min(num_docs, 50)):
                doc = store.get_document(i)
            
            elapsed_time = time.time() - start_time
            retrieval_rate = 50 / elapsed_time
            
            # Should handle at least 100 retrievals/second
            assert retrieval_rate > 100, f"Retrieval too slow: {retrieval_rate:.1f}/s"
            
        except ImportError:
            pytest.skip("Document store not available")
    
    def test_search_engine_latency(self):
        """Benchmark search engine query latency"""
        try:
            from venom.knowledge.search import SemanticSearch
            
            search = SemanticSearch()
            
            # Populate with test data
            test_queries = [
                "artificial intelligence",
                "machine learning algorithms",
                "neural network architectures",
                "deep learning frameworks",
                "natural language processing"
            ]
            
            latencies = []
            
            for query in test_queries:
                start_time = time.time()
                results = search.search(query, top_k=10)
                latency = time.time() - start_time
                latencies.append(latency)
            
            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            
            # Performance assertions
            assert avg_latency < 0.1, f"Average latency too high: {avg_latency:.3f}s"
            assert max_latency < 0.5, f"Max latency too high: {max_latency:.3f}s"
            
        except ImportError:
            pytest.skip("Search engine not available")
    
    def test_graph_traversal_speed(self):
        """Benchmark knowledge graph traversal performance"""
        try:
            from venom.knowledge.graph import KnowledgeGraph
            
            graph = KnowledgeGraph()
            
            # Create test graph with 100 nodes
            num_nodes = 100
            for i in range(num_nodes):
                graph.add_node(f"node_{i}", {"index": i})
            
            # Create edges (each node connects to next 5)
            for i in range(num_nodes - 5):
                for j in range(1, 6):
                    graph.add_edge(f"node_{i}", f"node_{i+j}", {"weight": 1.0})
            
            # Benchmark neighbor queries
            start_time = time.time()
            
            for i in range(50):
                neighbors = graph.get_neighbors(f"node_{i}")
                assert len(neighbors) > 0
            
            elapsed_time = time.time() - start_time
            queries_per_second = 50 / elapsed_time
            
            # Should handle at least 1000 queries/second
            assert queries_per_second > 1000, f"Too slow: {queries_per_second:.1f} q/s"
            
            # Benchmark path finding
            start_time = time.time()
            
            for i in range(10):
                path = graph.find_path(f"node_{i}", f"node_{i+10}")
            
            elapsed_time = time.time() - start_time
            path_finds_per_second = 10 / elapsed_time
            
            # Should handle at least 50 path finds/second
            assert path_finds_per_second > 50, f"Path finding too slow: {path_finds_per_second:.1f}/s"
            
        except ImportError:
            pytest.skip("Knowledge graph not available")
    
    def test_ai_inference_throughput(self):
        """Benchmark AI model inference throughput"""
        try:
            import torch
            from venom.inference.entropy_model import EntropyModel
            
            model = EntropyModel(ml_weight=0.12)
            
            # Prepare test data
            num_inferences = 100
            test_data = [torch.tensor([[float(i)]]) for i in range(num_inferences)]
            
            # Benchmark inference
            start_time = time.time()
            
            for data in test_data:
                prediction = model.forward(data)
                assert prediction is not None
            
            elapsed_time = time.time() - start_time
            inferences_per_second = num_inferences / elapsed_time
            
            # Should handle at least 500 inferences/second
            assert inferences_per_second > 500, f"Inference too slow: {inferences_per_second:.1f}/s"
            
        except ImportError:
            pytest.skip("Inference modules not available")
    
    def test_concurrent_operations(self):
        """Benchmark concurrent operation handling"""
        try:
            from venom.deployment.parallel_executor import ParallelWaveExecutor
            import concurrent.futures
            
            executor = ParallelWaveExecutor()
            
            # Create test waves with multiple tasks
            waves = []
            num_waves = 10
            tasks_per_wave = 10
            
            for wave_id in range(num_waves):
                tasks = []
                for task_id in range(tasks_per_wave):
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
            
            # Benchmark parallel execution
            start_time = time.time()
            result = executor.execute_parallel(waves)
            elapsed_time = time.time() - start_time
            
            total_tasks = num_waves * tasks_per_wave
            tasks_per_second = total_tasks / elapsed_time
            
            # Verify completion
            assert result.completed_tasks == total_tasks
            
            # Should achieve speedup from parallelism (relaxed for CI environments)
            # In CI or with mock tasks, speedup might be minimal
            assert result.speedup >= 1.0, f"Negative speedup: {result.speedup:.2f}x"
            
            # Should handle at least 3 tasks/second (relaxed for CI)
            assert tasks_per_second > 3, f"Too slow: {tasks_per_second:.1f} tasks/s"
            
        except ImportError:
            pytest.skip("Parallel executor not available")


class TestScalabilityBenchmarks:
    """Test scalability characteristics"""
    
    def test_document_store_scaling(self):
        """Test document store performance with increasing load"""
        try:
            from venom.knowledge.document_store import DocumentStore
            
            store = DocumentStore()
            
            # Test with different dataset sizes
            sizes = [10, 50, 100]
            throughputs = []
            
            for size in sizes:
                start_time = time.time()
                
                for i in range(size):
                    store.add_document(f"Content {i}", {"size": size})
                
                elapsed = time.time() - start_time
                throughput = size / elapsed
                throughputs.append(throughput)
            
            # Verify scalability: throughput should not degrade significantly
            # Allow up to 50% degradation
            assert throughputs[-1] > throughputs[0] * 0.5, "Performance degrades too much with scale"
            
        except ImportError:
            pytest.skip("Document store not available")
    
    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        try:
            import concurrent.futures
            from venom.observability.theta_monitor import ThetaMonitor
            
            monitor = ThetaMonitor(interval=0.1)
            monitor.start_monitoring()
            
            # Simulate concurrent status checks
            num_concurrent = 20
            
            def get_status():
                return monitor.get_current_metrics()
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_status) for _ in range(num_concurrent)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            elapsed = time.time() - start_time
            requests_per_second = num_concurrent / elapsed
            
            # All requests should complete successfully
            assert len(results) == num_concurrent
            
            # Should handle at least 50 concurrent requests/second
            assert requests_per_second > 50, f"Concurrent handling too slow: {requests_per_second:.1f}/s"
            
            monitor.stop_monitoring()
            
        except ImportError:
            pytest.skip("Monitoring modules not available")
    
    def test_memory_efficiency(self):
        """Test memory efficiency under load"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Measure initial memory
            initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Perform memory-intensive operations
            from venom.knowledge.document_store import DocumentStore
            store = DocumentStore()
            
            for i in range(100):
                store.add_document(f"Large document content " * 100, {"index": i})
            
            # Measure final memory
            final_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for 100 docs)
            assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
            
        except ImportError:
            pytest.skip("Required modules not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
