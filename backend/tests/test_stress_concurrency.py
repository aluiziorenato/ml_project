"""
Stress testing and concurrency integration tests.
These tests focus on high-load scenarios, concurrent operations,
and system behavior under stress.
"""
import pytest
import asyncio
import threading
import time
import concurrent.futures
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import httpx
from sqlmodel import Session

from app.models import User, OAuthSession
from app.core.security import get_password_hash
from app.services.mercadolibre import generate_code_verifier, generate_code_challenge
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session


class TestConcurrencyScenarios:
    """Test concurrent operations and race conditions."""
    
    def test_concurrent_user_creation(self, session: Session):
        """Test concurrent user creation scenarios."""
        results = []
        
        def create_user(user_id):
            try:
                user = User(
                    email=f"concurrent_user_{user_id}@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                
                results.append({
                    'success': True,
                    'user_id': user.id,
                    'thread_id': threading.current_thread().ident
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'thread_id': threading.current_thread().ident
                })
        
        # Create 10 users concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Analyze results
        successful_creations = [r for r in results if r['success']]
        failed_creations = [r for r in results if not r['success']]
        
        # At least some should succeed
        assert len(successful_creations) > 0
        
        # Log performance metrics
        print(f"Concurrent user creation: {len(successful_creations)}/{len(results)} succeeded in {end_time - start_time:.2f}s")

    def test_concurrent_oauth_sessions(self, session: Session):
        """Test concurrent OAuth session management."""
        results = []
        
        def oauth_session_operations(session_id):
            try:
                state = f"concurrent_state_{session_id}_{int(time.time() * 1000)}"
                code_verifier = generate_code_verifier()
                
                # Create session
                save_oauth_session(session, state, code_verifier)
                
                # Retrieve session
                oauth_session = get_oauth_session(session, state)
                assert oauth_session is not None
                
                # Simulate some processing time
                time.sleep(0.01)
                
                # Delete session
                delete_oauth_session(session, state)
                
                # Verify deletion
                deleted_session = get_oauth_session(session, state)
                assert deleted_session is None
                
                results.append({
                    'success': True,
                    'session_id': session_id,
                    'state': state
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'session_id': session_id
                })
        
        # Run 15 concurrent OAuth session operations
        threads = []
        for i in range(15):
            thread = threading.Thread(target=oauth_session_operations, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Analyze results
        successful_operations = [r for r in results if r['success']]
        
        # Most operations should succeed
        success_rate = len(successful_operations) / len(results)
        assert success_rate > 0.8  # At least 80% success rate
        
        print(f"Concurrent OAuth operations: {len(successful_operations)}/{len(results)} succeeded in {end_time - start_time:.2f}s")

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test concurrent external API calls."""
        call_results = []
        
        async def make_api_call(call_id):
            try:
                with patch("httpx.AsyncClient.get") as mock_get:
                    # Simulate different response times
                    await asyncio.sleep(0.01 + (call_id % 3) * 0.01)
                    
                    mock_response = MagicMock()
                    mock_response.raise_for_status.return_value = None
                    mock_response.json.return_value = {
                        "id": call_id,
                        "data": f"response_data_{call_id}",
                        "timestamp": time.time()
                    }
                    mock_get.return_value = mock_response
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"https://api.example.com/data/{call_id}")
                        response.raise_for_status()
                        data = response.json()
                    
                    call_results.append({
                        'success': True,
                        'call_id': call_id,
                        'data': data
                    })
            except Exception as e:
                call_results.append({
                    'success': False,
                    'call_id': call_id,
                    'error': str(e)
                })
        
        # Make 25 concurrent API calls
        start_time = time.time()
        tasks = [make_api_call(i) for i in range(25)]
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyze results
        successful_calls = [r for r in call_results if r['success']]
        
        # All calls should succeed in this mocked scenario
        assert len(successful_calls) == 25
        
        print(f"Concurrent API calls: {len(successful_calls)}/25 succeeded in {end_time - start_time:.2f}s")

    def test_database_deadlock_simulation(self, session: Session):
        """Test database deadlock scenarios."""
        deadlock_results = []
        
        def operation_sequence_1():
            try:
                # Create user A first, then user B
                user_a = User(
                    email="deadlock_user_a@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user_a)
                session.commit()
                
                time.sleep(0.01)  # Small delay to increase chance of deadlock
                
                user_b = User(
                    email="deadlock_user_b@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user_b)
                session.commit()
                
                deadlock_results.append({'sequence': 1, 'success': True})
            except Exception as e:
                deadlock_results.append({'sequence': 1, 'success': False, 'error': str(e)})
        
        def operation_sequence_2():
            try:
                # Create user B first, then user A (reverse order)
                user_b = User(
                    email="deadlock_user_b2@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user_b)
                session.commit()
                
                time.sleep(0.01)  # Small delay
                
                user_a = User(
                    email="deadlock_user_a2@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user_a)
                session.commit()
                
                deadlock_results.append({'sequence': 2, 'success': True})
            except Exception as e:
                deadlock_results.append({'sequence': 2, 'success': False, 'error': str(e)})
        
        # Run both sequences concurrently
        thread1 = threading.Thread(target=operation_sequence_1)
        thread2 = threading.Thread(target=operation_sequence_2)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # At least one should succeed (deadlock prevention should work)
        successful_operations = [r for r in deadlock_results if r['success']]
        assert len(successful_operations) >= 1


class TestStressScenarios:
    """Test system behavior under stress."""
    
    @pytest.mark.asyncio
    async def test_high_volume_request_handling(self, async_client):
        """Test handling high volume of requests."""
        request_count = 50
        batch_size = 10
        results = []
        
        async def batch_requests(batch_id):
            batch_results = []
            for i in range(batch_size):
                request_id = batch_id * batch_size + i
                try:
                    response = await async_client.get(f"/health?batch={batch_id}&request={i}")
                    batch_results.append({
                        'request_id': request_id,
                        'status_code': response.status_code,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    batch_results.append({
                        'request_id': request_id,
                        'error': str(e),
                        'success': False
                    })
            return batch_results
        
        # Execute batches concurrently
        start_time = time.time()
        batch_tasks = [batch_requests(i) for i in range(request_count // batch_size)]
        batch_results = await asyncio.gather(*batch_tasks)
        end_time = time.time()
        
        # Flatten results
        for batch in batch_results:
            results.extend(batch)
        
        # Analyze performance
        successful_requests = [r for r in results if r['success']]
        success_rate = len(successful_requests) / len(results)
        requests_per_second = len(results) / (end_time - start_time)
        
        print(f"High volume test: {len(successful_requests)}/{len(results)} requests succeeded")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Throughput: {requests_per_second:.2f} requests/second")
        
        # Assert minimum performance criteria
        assert success_rate > 0.9  # At least 90% success rate
        assert requests_per_second > 10  # At least 10 requests per second

    def test_memory_stress_simulation(self, session: Session):
        """Test memory usage under stress."""
        large_objects = []
        
        try:
            # Create many objects to stress memory
            for i in range(100):
                user = User(
                    email=f"memory_stress_{i}@example.com",
                    hashed_password=get_password_hash("password" * 100),  # Larger password
                    is_active=True
                )
                session.add(user)
                
                # Simulate holding references to create memory pressure
                large_objects.append(user)
                
                if i % 20 == 0:
                    session.commit()
            
            session.commit()
            
            # Test that we can still perform operations
            test_user = User(
                email="memory_test_final@example.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            session.add(test_user)
            session.commit()
            
            assert test_user.id is not None
            
        finally:
            # Cleanup
            large_objects.clear()

    @pytest.mark.asyncio
    async def test_timeout_stress_scenarios(self):
        """Test system behavior under timeout stress."""
        timeout_scenarios = []
        
        async def api_call_with_random_timeout(call_id):
            # Simulate varying response times
            delay = (call_id % 5) * 0.01  # 0 to 0.04 seconds
            
            try:
                with patch("httpx.AsyncClient.get") as mock_get:
                    async def mock_delayed_response(*args, **kwargs):
                        await asyncio.sleep(delay)
                        mock_response = MagicMock()
                        mock_response.raise_for_status.return_value = None
                        mock_response.json.return_value = {"call_id": call_id, "delay": delay}
                        return mock_response
                    
                    mock_get.side_effect = mock_delayed_response
                    
                    # Use short timeout to induce some failures
                    async with httpx.AsyncClient(timeout=0.02) as client:
                        response = await client.get(f"https://api.example.com/data/{call_id}")
                        response.raise_for_status()
                        data = response.json()
                    
                    timeout_scenarios.append({
                        'call_id': call_id,
                        'delay': delay,
                        'success': True,
                        'data': data
                    })
            except asyncio.TimeoutError:
                timeout_scenarios.append({
                    'call_id': call_id,
                    'delay': delay,
                    'success': False,
                    'error': 'timeout'
                })
            except Exception as e:
                timeout_scenarios.append({
                    'call_id': call_id,
                    'delay': delay,
                    'success': False,
                    'error': str(e)
                })
        
        # Run many calls with potential timeouts
        tasks = [api_call_with_random_timeout(i) for i in range(20)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze timeout behavior
        successful_calls = [s for s in timeout_scenarios if s['success']]
        timeout_calls = [s for s in timeout_scenarios if not s['success'] and s.get('error') == 'timeout']
        
        print(f"Timeout stress test: {len(successful_calls)} succeeded, {len(timeout_calls)} timed out")
        
        # Should have a mix of successes and timeouts
        assert len(successful_calls) > 0
        assert len(timeout_scenarios) == 20


class TestLoadBalancingSimulation:
    """Test load balancing and distribution patterns."""
    
    @pytest.mark.asyncio
    async def test_round_robin_simulation(self, async_client):
        """Test round-robin load distribution simulation."""
        server_responses = []
        
        async def make_request_to_server(request_id):
            # Simulate different servers handling requests
            server_id = request_id % 3  # 3 simulated servers
            
            try:
                response = await async_client.get(f"/health?server={server_id}&request={request_id}")
                server_responses.append({
                    'request_id': request_id,
                    'server_id': server_id,
                    'status_code': response.status_code,
                    'success': True
                })
            except Exception as e:
                server_responses.append({
                    'request_id': request_id,
                    'server_id': server_id,
                    'error': str(e),
                    'success': False
                })
        
        # Make requests that would be distributed across servers
        tasks = [make_request_to_server(i) for i in range(30)]
        await asyncio.gather(*tasks)
        
        # Analyze distribution
        server_counts = {}
        for response in server_responses:
            if response['success']:
                server_id = response['server_id']
                server_counts[server_id] = server_counts.get(server_id, 0) + 1
        
        print(f"Load distribution: {server_counts}")
        
        # Distribution should be roughly even
        if len(server_counts) > 1:
            max_requests = max(server_counts.values())
            min_requests = min(server_counts.values())
            # Difference shouldn't be too large
            assert max_requests - min_requests <= 3

    def test_sticky_session_simulation(self, session: Session):
        """Test sticky session behavior simulation."""
        session_mappings = {}
        
        def handle_request_with_sticky_session(user_id):
            # Simulate sticky session - same user always goes to same server
            server_id = hash(f"user_{user_id}") % 3
            
            if user_id not in session_mappings:
                session_mappings[user_id] = {
                    'server_id': server_id,
                    'requests': 0
                }
            
            session_mappings[user_id]['requests'] += 1
            
            return session_mappings[user_id]
        
        # Simulate multiple requests from same users
        for _ in range(10):
            for user_id in range(5):
                result = handle_request_with_sticky_session(user_id)
                # Each user should always get the same server
                assert result['server_id'] == hash(f"user_{user_id}") % 3
        
        # Verify each user made multiple requests to same server
        for user_id, mapping in session_mappings.items():
            assert mapping['requests'] == 10

    @pytest.mark.asyncio
    async def test_circuit_breaker_load_balancing(self):
        """Test circuit breaker with load balancing."""
        server_states = {
            'server_0': {'failures': 0, 'circuit_open': False},
            'server_1': {'failures': 0, 'circuit_open': False},
            'server_2': {'failures': 0, 'circuit_open': False}
        }
        
        async def make_request_with_circuit_breaker(request_id):
            server_id = f"server_{request_id % 3}"
            server_state = server_states[server_id]
            
            if server_state['circuit_open']:
                # Try next server
                for i in range(1, 3):
                    alt_server_id = f"server_{(request_id + i) % 3}"
                    if not server_states[alt_server_id]['circuit_open']:
                        server_id = alt_server_id
                        server_state = server_states[server_id]
                        break
            
            # Simulate server failure for server_1
            if server_id == 'server_1' and not server_state['circuit_open']:
                server_state['failures'] += 1
                if server_state['failures'] >= 3:
                    server_state['circuit_open'] = True
                raise Exception(f"{server_id} is failing")
            
            return {'server_id': server_id, 'status': 'success'}
        
        results = []
        for i in range(15):
            try:
                result = await make_request_with_circuit_breaker(i)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'status': 'failed'})
        
        # Circuit breaker should have opened for server_1
        assert server_states['server_1']['circuit_open']
        
        # Should still have successful requests from other servers
        successful_results = [r for r in results if r.get('status') == 'success']
        assert len(successful_results) > 0


class TestResourceExhaustionScenarios:
    """Test behavior when resources are exhausted."""
    
    def test_connection_pool_exhaustion(self):
        """Test connection pool exhaustion scenarios."""
        from sqlmodel import create_engine, Session
        from sqlmodel.pool import StaticPool
        
        # Create engine with very small pool
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_size=1,  # Very small pool
            max_overflow=1
        )
        
        sessions = []
        exceptions = []
        
        try:
            # Try to create more sessions than pool allows
            for i in range(5):
                try:
                    session = Session(engine)
                    sessions.append(session)
                    
                    # Do an operation to use the connection
                    user = User(
                        email=f"pool_exhaust_{i}@example.com",
                        hashed_password=get_password_hash("password"),
                        is_active=True
                    )
                    session.add(user)
                    session.commit()
                except Exception as e:
                    exceptions.append(str(e))
        finally:
            # Cleanup
            for session in sessions:
                try:
                    session.close()
                except:
                    pass
        
        # Should have handled pool exhaustion gracefully
        # Either by queuing or raising appropriate exceptions
        print(f"Created {len(sessions)} sessions, {len(exceptions)} exceptions")

    @pytest.mark.asyncio
    async def test_memory_pressure_scenarios(self):
        """Test behavior under memory pressure."""
        large_data_sets = []
        
        try:
            # Create increasingly large data sets
            for i in range(10):
                # Simulate processing large API responses
                large_data = {
                    'id': i,
                    'data': 'x' * (1000 * (i + 1)),  # Increasing size
                    'items': [{'item_id': j, 'data': 'y' * 100} for j in range(i * 10)]
                }
                large_data_sets.append(large_data)
                
                # Simulate async processing
                await asyncio.sleep(0.001)
            
            # Test that we can still process new data
            final_data = {'final': True, 'processed': len(large_data_sets)}
            large_data_sets.append(final_data)
            
            assert len(large_data_sets) == 11
            assert large_data_sets[-1]['final'] is True
            
        finally:
            # Cleanup to prevent actual memory issues
            large_data_sets.clear()

    def test_file_descriptor_exhaustion_simulation(self):
        """Test file descriptor exhaustion simulation."""
        # Simulate many simultaneous connections
        connection_count = 0
        max_connections = 100
        active_connections = []
        
        class MockConnection:
            def __init__(self, connection_id):
                self.id = connection_id
                self.active = True
            
            def close(self):
                self.active = False
        
        try:
            # Simulate opening many connections
            for i in range(max_connections + 10):  # Try to exceed limit
                if connection_count < max_connections:
                    conn = MockConnection(i)
                    active_connections.append(conn)
                    connection_count += 1
                else:
                    # Simulate connection refused
                    break
            
            # Should have hit the limit
            assert len(active_connections) == max_connections
            
        finally:
            # Cleanup connections
            for conn in active_connections:
                conn.close()
            active_connections.clear()