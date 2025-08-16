"""
Performance tests for memory usage monitoring and optimization.
"""
import pytest
import time
import threading
import queue
import gc
import psutil
import os
from fastapi.testclient import TestClient
from sqlmodel import Session
from memory_profiler import profile
import sys
from io import StringIO


@pytest.mark.performance
class TestMemoryUsageMonitoring:
    """Test comprehensive memory usage monitoring."""
    
    def test_baseline_memory_usage(self, client: TestClient, memory_monitor):
        """Test baseline memory usage without operations."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Wait a bit to establish baseline
        time.sleep(2)
        
        # Measure baseline memory
        baseline_memory = process.memory_info().rss
        baseline_increase = (baseline_memory - initial_memory) / 1024 / 1024  # MB
        
        # Make a single simple request
        response = client.get("/health")
        assert response.status_code == 200
        
        # Measure memory after simple request
        after_request_memory = process.memory_info().rss
        request_memory_increase = (after_request_memory - baseline_memory) / 1024 / 1024  # MB
        
        # Baseline assertions
        assert baseline_increase < 10, f"Baseline memory increase {baseline_increase:.1f}MB too high"
        assert request_memory_increase < 5, f"Single request memory increase {request_memory_increase:.1f}MB too high"
        
    def test_memory_usage_during_seo_operations(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test memory usage during SEO operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        memory_snapshots = []
        
        # Perform SEO operations with memory monitoring
        for i in range(50):
            seo_data = {
                "text": f"Memory monitoring test {i}: Comprehensive product description with detailed features, specifications, benefits, and usage scenarios for testing memory consumption patterns during SEO optimization operations.",
                "max_length": 200 + (i % 100),  # Varying lengths
                "keywords": [f"keyword{j}" for j in range(i % 10)]  # Varying keyword counts
            }
            
            # Memory before request
            before_memory = process.memory_info().rss
            
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert response.status_code == 200
            
            # Memory after request
            after_memory = process.memory_info().rss
            
            memory_snapshots.append({
                "iteration": i,
                "before_memory_mb": (before_memory - initial_memory) / 1024 / 1024,
                "after_memory_mb": (after_memory - initial_memory) / 1024 / 1024,
                "request_memory_delta_mb": (after_memory - before_memory) / 1024 / 1024
            })
            
            # Periodic garbage collection
            if i % 10 == 0:
                gc.collect()
                
        # Analyze memory usage patterns
        max_memory_usage = max(snapshot["after_memory_mb"] for snapshot in memory_snapshots)
        avg_memory_usage = sum(snapshot["after_memory_mb"] for snapshot in memory_snapshots) / len(memory_snapshots)
        final_memory_usage = memory_snapshots[-1]["after_memory_mb"]
        
        # Calculate memory growth trend
        first_10_avg = sum(snapshot["after_memory_mb"] for snapshot in memory_snapshots[:10]) / 10
        last_10_avg = sum(snapshot["after_memory_mb"] for snapshot in memory_snapshots[-10:]) / 10
        memory_growth_rate = (last_10_avg - first_10_avg) / first_10_avg if first_10_avg > 0 else 0
        
        # Memory usage assertions
        assert max_memory_usage < 200, f"Peak memory usage {max_memory_usage:.1f}MB exceeds 200MB"
        assert avg_memory_usage < 100, f"Average memory usage {avg_memory_usage:.1f}MB exceeds 100MB"
        assert final_memory_usage < 150, f"Final memory usage {final_memory_usage:.1f}MB exceeds 150MB"
        assert memory_growth_rate < 0.3, f"Memory growth rate {memory_growth_rate:.2%} indicates potential leak"
        
    def test_memory_usage_under_concurrent_load(self, client: TestClient, memory_monitor):
        """Test memory usage under concurrent load conditions."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        memory_samples = []
        load_active = threading.Event()
        load_active.set()
        
        def memory_sampler():
            """Continuously sample memory usage during load test."""
            while load_active.is_set():
                current_memory = process.memory_info().rss
                memory_increase = (current_memory - initial_memory) / 1024 / 1024
                
                memory_samples.append({
                    "timestamp": time.time(),
                    "memory_mb": memory_increase,
                    "rss_bytes": current_memory
                })
                
                time.sleep(0.1)  # Sample every 100ms
                
        def load_generator(worker_id, num_requests):
            """Generate load to test memory usage."""
            for i in range(num_requests):
                try:
                    response = client.get("/health")
                    assert response.status_code == 200
                except Exception:
                    pass  # Continue load even if some requests fail
                    
                time.sleep(0.01)  # Small delay between requests
                
        # Start memory sampling
        memory_thread = threading.Thread(target=memory_sampler)
        memory_thread.start()
        
        # Start load generators
        num_workers = 10
        requests_per_worker = 100
        load_threads = []
        
        load_start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=load_generator, args=(worker_id, requests_per_worker))
            load_threads.append(thread)
            thread.start()
            
        # Wait for load to complete
        for thread in load_threads:
            thread.join()
            
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time
        
        # Stop memory sampling
        load_active.clear()
        memory_thread.join(timeout=5)
        
        # Analyze memory usage during load
        if memory_samples:
            memory_values = [sample["memory_mb"] for sample in memory_samples]
            peak_memory = max(memory_values)
            avg_memory = sum(memory_values) / len(memory_values)
            final_memory = memory_values[-1]
            
            # Calculate memory stability
            memory_variance = sum((m - avg_memory) ** 2 for m in memory_values) / len(memory_values)
            memory_std_dev = memory_variance ** 0.5
            
            # Memory performance under load assertions
            assert peak_memory < 300, f"Peak memory {peak_memory:.1f}MB under load exceeds 300MB"
            assert avg_memory < 150, f"Average memory {avg_memory:.1f}MB under load exceeds 150MB"
            assert final_memory < 200, f"Final memory {final_memory:.1f}MB after load exceeds 200MB"
            assert memory_std_dev < 50, f"Memory standard deviation {memory_std_dev:.1f}MB indicates instability"
            
        # Load performance should be maintained
        total_requests = num_workers * requests_per_worker
        throughput = total_requests / load_duration
        assert throughput >= 50, f"Throughput {throughput:.1f} req/s under memory monitoring below 50"
        
    def test_memory_fragmentation_detection(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test for memory fragmentation during various operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Get initial memory details if available
        try:
            initial_memory_info = process.memory_full_info()
            initial_vms = initial_memory_info.vms
            initial_rss = initial_memory_info.rss
        except AttributeError:
            # Fallback to basic memory info
            initial_memory_info = process.memory_info()
            initial_vms = initial_memory_info.vms if hasattr(initial_memory_info, 'vms') else 0
            initial_rss = initial_memory_info.rss
            
        fragmentation_data = []
        
        # Perform operations that might cause fragmentation
        operation_types = [
            {"name": "small_seo", "text": "Short product description", "max_length": 50},
            {"name": "large_seo", "text": "Very long detailed product description " * 20, "max_length": 500},
            {"name": "medium_seo", "text": "Medium length product description with features", "max_length": 160}
        ]
        
        for cycle in range(10):
            for op_type in operation_types:
                # Perform operation
                response = client.post("/api/seo/optimize", json=op_type, headers=auth_headers)
                assert response.status_code == 200
                
                # Measure memory
                try:
                    current_memory_info = process.memory_full_info()
                    current_vms = current_memory_info.vms
                    current_rss = current_memory_info.rss
                except AttributeError:
                    current_memory_info = process.memory_info()
                    current_vms = current_memory_info.vms if hasattr(current_memory_info, 'vms') else 0
                    current_rss = current_memory_info.rss
                    
                # Calculate fragmentation indicator
                vms_increase = (current_vms - initial_vms) / 1024 / 1024  # MB
                rss_increase = (current_rss - initial_rss) / 1024 / 1024  # MB
                fragmentation_ratio = vms_increase / rss_increase if rss_increase > 0 else 1
                
                fragmentation_data.append({
                    "cycle": cycle,
                    "operation": op_type["name"],
                    "vms_increase_mb": vms_increase,
                    "rss_increase_mb": rss_increase,
                    "fragmentation_ratio": fragmentation_ratio
                })
                
        # Analyze fragmentation
        if fragmentation_data:
            avg_fragmentation_ratio = sum(d["fragmentation_ratio"] for d in fragmentation_data) / len(fragmentation_data)
            max_fragmentation_ratio = max(d["fragmentation_ratio"] for d in fragmentation_data)
            final_vms_increase = fragmentation_data[-1]["vms_increase_mb"]
            final_rss_increase = fragmentation_data[-1]["rss_increase_mb"]
            
            # Fragmentation assertions
            assert avg_fragmentation_ratio < 3.0, f"Average fragmentation ratio {avg_fragmentation_ratio:.2f} too high"
            assert max_fragmentation_ratio < 5.0, f"Max fragmentation ratio {max_fragmentation_ratio:.2f} too high"
            assert final_vms_increase < 500, f"Final VMS increase {final_vms_increase:.1f}MB too high"
            assert final_rss_increase < 200, f"Final RSS increase {final_rss_increase:.1f}MB too high"
            
    def test_garbage_collection_efficiency(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test garbage collection efficiency during operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        gc_cycles_data = []
        
        for gc_cycle in range(5):
            # Phase 1: Generate garbage
            pre_gc_memory = process.memory_info().rss
            
            for i in range(100):
                # Create operations that should generate garbage
                large_seo_data = {
                    "text": f"Garbage collection test cycle {gc_cycle} iteration {i}: " + "Large content " * 50,
                    "max_length": 300,
                    "keywords": [f"gc_keyword_{j}" for j in range(20)]
                }
                
                response = client.post("/api/seo/optimize", json=large_seo_data, headers=auth_headers)
                assert response.status_code == 200
                
            # Measure memory before GC
            before_gc_memory = process.memory_info().rss
            before_gc_increase = (before_gc_memory - initial_memory) / 1024 / 1024
            
            # Phase 2: Force garbage collection
            gc_start_time = time.time()
            collected_objects = gc.collect()
            gc_duration = time.time() - gc_start_time
            
            # Small delay for system cleanup
            time.sleep(0.5)
            
            # Measure memory after GC
            after_gc_memory = process.memory_info().rss
            after_gc_increase = (after_gc_memory - initial_memory) / 1024 / 1024
            
            memory_freed = (before_gc_memory - after_gc_memory) / 1024 / 1024
            gc_efficiency = memory_freed / before_gc_increase if before_gc_increase > 0 else 0
            
            gc_cycles_data.append({
                "cycle": gc_cycle,
                "before_gc_mb": before_gc_increase,
                "after_gc_mb": after_gc_increase,
                "memory_freed_mb": memory_freed,
                "gc_efficiency": gc_efficiency,
                "collected_objects": collected_objects,
                "gc_duration": gc_duration
            })
            
        # Analyze GC efficiency
        avg_gc_efficiency = sum(d["gc_efficiency"] for d in gc_cycles_data) / len(gc_cycles_data)
        total_memory_freed = sum(d["memory_freed_mb"] for d in gc_cycles_data)
        avg_gc_duration = sum(d["gc_duration"] for d in gc_cycles_data) / len(gc_cycles_data)
        final_memory_after_all_gc = gc_cycles_data[-1]["after_gc_mb"]
        
        # GC efficiency assertions
        assert avg_gc_efficiency >= 0.1, f"Average GC efficiency {avg_gc_efficiency:.2%} too low"
        assert total_memory_freed >= 0, f"Total memory freed {total_memory_freed:.1f}MB negative"
        assert avg_gc_duration < 1.0, f"Average GC duration {avg_gc_duration:.3f}s too long"
        assert final_memory_after_all_gc < 300, f"Final memory {final_memory_after_all_gc:.1f}MB after GC too high"
        
        # Check that GC is actually working
        memory_increases_before_gc = [d["before_gc_mb"] for d in gc_cycles_data]
        memory_increases_after_gc = [d["after_gc_mb"] for d in gc_cycles_data]
        
        # At least some GC cycles should show memory reduction
        effective_gc_cycles = sum(1 for d in gc_cycles_data if d["memory_freed_mb"] > 0)
        assert effective_gc_cycles >= len(gc_cycles_data) * 0.6, f"Only {effective_gc_cycles}/{len(gc_cycles_data)} GC cycles were effective"


@pytest.mark.performance
class TestMemoryLeakDetection:
    """Test for memory leaks in various scenarios."""
    
    def test_request_processing_memory_leak(self, client: TestClient, memory_monitor):
        """Test for memory leaks in request processing."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Perform multiple rounds of requests
        rounds = 10
        requests_per_round = 50
        round_memory_data = []
        
        for round_num in range(rounds):
            round_start_memory = process.memory_info().rss
            
            # Perform requests in this round
            for i in range(requests_per_round):
                response = client.get("/health")
                assert response.status_code == 200
                
            # Force cleanup between rounds
            gc.collect()
            time.sleep(0.5)
            
            round_end_memory = process.memory_info().rss
            round_memory_increase = (round_end_memory - initial_memory) / 1024 / 1024
            
            round_memory_data.append({
                "round": round_num,
                "memory_increase_mb": round_memory_increase,
                "requests_processed": requests_per_round
            })
            
        # Analyze for memory leaks
        memory_increases = [data["memory_increase_mb"] for data in round_memory_data]
        
        # Check for linear growth (leak indicator)
        if len(memory_increases) >= 5:
            # Calculate linear trend
            x_values = list(range(len(memory_increases)))
            n = len(memory_increases)
            
            x_mean = sum(x_values) / n
            y_mean = sum(memory_increases) / n
            
            # Linear regression slope
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, memory_increases))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            slope = numerator / denominator if denominator != 0 else 0
            
            # Leak detection assertions
            assert slope < 2.0, f"Memory growth slope {slope:.2f} MB/round indicates potential leak"
            
        # Memory should stabilize after initial allocation
        first_half_avg = sum(memory_increases[:len(memory_increases)//2]) / (len(memory_increases)//2)
        second_half_avg = sum(memory_increases[len(memory_increases)//2:]) / (len(memory_increases) - len(memory_increases)//2)
        
        growth_factor = second_half_avg / first_half_avg if first_half_avg > 0 else 1
        assert growth_factor < 1.5, f"Memory growth factor {growth_factor:.2f} indicates potential leak"
        
    def test_authentication_memory_leak(self, client: TestClient, db: Session, memory_monitor):
        """Test for memory leaks in authentication operations."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        from app.models import User
        from app.core.security import get_password_hash
        
        # Create test user
        test_user = User(
            email="memory_leak_auth@example.com",
            hashed_password=get_password_hash("MemoryTestPassword123!"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        
        auth_memory_data = []
        
        # Perform multiple authentication cycles
        for cycle in range(10):
            cycle_start_memory = process.memory_info().rss
            
            # Perform authentication operations
            for i in range(20):
                login_data = {
                    "username": "memory_leak_auth@example.com",
                    "password": "MemoryTestPassword123!"
                }
                
                response = client.post("/api/auth/token", data=login_data)
                # Should succeed or fail gracefully
                assert response.status_code in [200, 401, 422]
                
            # Cleanup between cycles
            gc.collect()
            time.sleep(0.5)
            
            cycle_end_memory = process.memory_info().rss
            cycle_memory_increase = (cycle_end_memory - initial_memory) / 1024 / 1024
            
            auth_memory_data.append({
                "cycle": cycle,
                "memory_increase_mb": cycle_memory_increase
            })
            
        # Analyze authentication memory usage
        memory_increases = [data["memory_increase_mb"] for data in auth_memory_data]
        
        # Check for memory stability in authentication
        max_memory_increase = max(memory_increases)
        final_memory_increase = memory_increases[-1]
        
        assert max_memory_increase < 100, f"Max auth memory increase {max_memory_increase:.1f}MB too high"
        assert final_memory_increase < 80, f"Final auth memory increase {final_memory_increase:.1f}MB too high"
        
        # Check for growth trend
        if len(memory_increases) >= 5:
            first_quarter_avg = sum(memory_increases[:len(memory_increases)//4]) / (len(memory_increases)//4)
            last_quarter_avg = sum(memory_increases[-len(memory_increases)//4:]) / (len(memory_increases)//4)
            
            auth_growth_rate = (last_quarter_avg - first_quarter_avg) / first_quarter_avg if first_quarter_avg > 0 else 0
            assert auth_growth_rate < 0.3, f"Auth memory growth rate {auth_growth_rate:.2%} indicates leak"
            
    def test_database_operation_memory_leak(self, engine, memory_monitor):
        """Test for memory leaks in database operations."""
        from sqlmodel import Session, text
        
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        db_memory_data = []
        
        # Perform multiple database operation cycles
        for cycle in range(8):
            cycle_start_memory = process.memory_info().rss
            
            # Perform database operations
            for i in range(100):
                with Session(engine) as session:
                    result = session.exec(text("SELECT 1, 'test_string', NOW()")).first()
                    assert result is not None
                    
            # Cleanup between cycles
            gc.collect()
            time.sleep(1)  # Longer delay for DB cleanup
            
            cycle_end_memory = process.memory_info().rss
            cycle_memory_increase = (cycle_end_memory - initial_memory) / 1024 / 1024
            
            db_memory_data.append({
                "cycle": cycle,
                "memory_increase_mb": cycle_memory_increase
            })
            
        # Analyze database memory usage
        memory_increases = [data["memory_increase_mb"] for data in db_memory_data]
        
        # Database operations should not cause significant memory growth
        max_db_memory = max(memory_increases)
        final_db_memory = memory_increases[-1]
        
        assert max_db_memory < 150, f"Max DB memory increase {max_db_memory:.1f}MB too high"
        assert final_db_memory < 100, f"Final DB memory increase {final_db_memory:.1f}MB too high"
        
        # Check for database memory leak pattern
        if len(memory_increases) >= 4:
            first_half_avg = sum(memory_increases[:len(memory_increases)//2]) / (len(memory_increases)//2)
            second_half_avg = sum(memory_increases[len(memory_increases)//2:]) / (len(memory_increases) - len(memory_increases)//2)
            
            db_growth_factor = second_half_avg / first_half_avg if first_half_avg > 0 else 1
            assert db_growth_factor < 1.3, f"DB memory growth factor {db_growth_factor:.2f} indicates leak"


@pytest.mark.performance
class TestMemoryOptimization:
    """Test memory optimization techniques and effectiveness."""
    
    def test_memory_optimization_effectiveness(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test effectiveness of memory optimization techniques."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        optimization_results = []
        
        # Test different optimization scenarios
        optimization_scenarios = [
            {
                "name": "baseline",
                "gc_frequency": 0,  # No forced GC
                "request_delay": 0.01
            },
            {
                "name": "frequent_gc",
                "gc_frequency": 10,  # GC every 10 requests
                "request_delay": 0.01
            },
            {
                "name": "delayed_requests",
                "gc_frequency": 0,
                "request_delay": 0.05  # Longer delay between requests
            }
        ]
        
        for scenario in optimization_scenarios:
            scenario_start_memory = process.memory_info().rss
            scenario_start_time = time.time()
            
            # Perform operations with optimization technique
            for i in range(100):
                seo_data = {
                    "text": f"Optimization test {scenario['name']} iteration {i}: " + "Content " * 20,
                    "max_length": 200
                }
                
                response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
                assert response.status_code == 200
                
                # Apply optimization technique
                if scenario["gc_frequency"] > 0 and i % scenario["gc_frequency"] == 0:
                    gc.collect()
                    
                if scenario["request_delay"] > 0:
                    time.sleep(scenario["request_delay"])
                    
            scenario_end_time = time.time()
            scenario_end_memory = process.memory_info().rss
            
            scenario_duration = scenario_end_time - scenario_start_time
            scenario_memory_increase = (scenario_end_memory - scenario_start_memory) / 1024 / 1024
            scenario_throughput = 100 / scenario_duration
            
            optimization_results.append({
                "scenario": scenario["name"],
                "memory_increase_mb": scenario_memory_increase,
                "duration_seconds": scenario_duration,
                "throughput_req_per_sec": scenario_throughput,
                "memory_efficiency": 1000 / scenario_memory_increase if scenario_memory_increase > 0 else float('inf')
            })
            
            # Cleanup between scenarios
            gc.collect()
            time.sleep(2)
            
        # Analyze optimization effectiveness
        baseline_result = next(r for r in optimization_results if r["scenario"] == "baseline")
        
        for result in optimization_results:
            if result["scenario"] != "baseline":
                # Compare with baseline
                memory_improvement = (baseline_result["memory_increase_mb"] - result["memory_increase_mb"]) / baseline_result["memory_increase_mb"]
                throughput_ratio = result["throughput_req_per_sec"] / baseline_result["throughput_req_per_sec"]
                
                # Optimization should either reduce memory usage or maintain acceptable performance
                if result["scenario"] == "frequent_gc":
                    # Frequent GC might reduce memory but impact performance
                    assert memory_improvement >= -0.5, f"Frequent GC increased memory by {-memory_improvement:.2%}"
                    assert throughput_ratio >= 0.5, f"Frequent GC reduced throughput to {throughput_ratio:.2%} of baseline"
                    
                elif result["scenario"] == "delayed_requests":
                    # Delayed requests should reduce memory pressure
                    assert result["memory_increase_mb"] <= baseline_result["memory_increase_mb"] * 1.2, \
                        f"Delayed requests didn't help memory usage"
                        
        # Overall memory usage should be reasonable
        max_memory_usage = max(r["memory_increase_mb"] for r in optimization_results)
        assert max_memory_usage < 200, f"Max memory usage {max_memory_usage:.1f}MB across scenarios too high"
        
    def test_memory_pool_efficiency(self, client: TestClient, memory_monitor):
        """Test memory pool efficiency during repeated operations."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Warm up to establish memory pools
        for i in range(20):
            response = client.get("/health")
            assert response.status_code == 200
            
        # Measure memory after warmup
        warmup_memory = process.memory_info().rss
        warmup_increase = (warmup_memory - initial_memory) / 1024 / 1024
        
        # Perform repeated operations to test pool efficiency
        pool_test_start_memory = process.memory_info().rss
        
        for i in range(200):
            response = client.get("/health")
            assert response.status_code == 200
            
        pool_test_end_memory = process.memory_info().rss
        pool_test_increase = (pool_test_end_memory - pool_test_start_memory) / 1024 / 1024
        
        # Memory pool efficiency assertions
        assert warmup_increase < 50, f"Warmup memory increase {warmup_increase:.1f}MB too high"
        assert pool_test_increase < 20, f"Pool test memory increase {pool_test_increase:.1f}MB indicates poor pooling"
        
        # Memory usage should be stable after warmup
        stability_ratio = pool_test_increase / warmup_increase if warmup_increase > 0 else 0
        assert stability_ratio < 0.5, f"Memory not stable after warmup, ratio {stability_ratio:.2f}"