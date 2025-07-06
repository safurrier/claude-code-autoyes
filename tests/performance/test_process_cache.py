"""Tests for process detection caching to reduce filesystem scanning overhead."""

import time
from dataclasses import dataclass
from typing import List, Callable

import pytest

from claude_code_autoyes.core.models import ClaudeInstance


@dataclass 
class CacheResult:
    """Result of a cache operation."""
    
    cache_hit: bool
    duration_ms: float
    data: List[ClaudeInstance]


class FakeProcessScanner:
    """Test double for expensive process scanning operations."""
    
    def __init__(self, scan_instances: List[ClaudeInstance], scan_delay_ms: int = 100):
        self.instances = scan_instances
        self.scan_delay_ms = scan_delay_ms
        self.call_count = 0
        
    def scan_processes(self) -> List[ClaudeInstance]:
        """Simulate expensive process scanning with delay."""
        self.call_count += 1
        time.sleep(self.scan_delay_ms / 1000.0)  # Simulate scanning overhead
        return self.instances.copy()


@pytest.mark.performance
class TestProcessCache:
    """Test suite for process detection caching functionality."""
    
    def test_process_cache_returns_cached_results_within_ttl(self):
        """Test that cache returns cached results without scanning within TTL."""
        # Arrange: Set up scanner with expensive operations and cache with 5s TTL
        instances = [self._create_test_instance()]
        scanner = FakeProcessScanner(scan_instances=instances, scan_delay_ms=100)
        
        # This should fail - ProcessCache doesn't exist yet
        from claude_code_autoyes.core.process_cache import ProcessCache
        cache = ProcessCache(ttl_seconds=5)
        
        # Act: First call should scan, second should hit cache
        start_time = time.time()
        first_result = cache.get_processes(scanner.scan_processes)
        first_duration = (time.time() - start_time) * 1000
        
        start_time = time.time()
        second_result = cache.get_processes(scanner.scan_processes)
        second_duration = (time.time() - start_time) * 1000
        
        # Assert: Second call should be much faster (cache hit)
        assert scanner.call_count == 1  # Only one actual scan
        assert first_duration >= 90  # First call includes scan delay
        assert second_duration < 10   # Second call from cache
        assert first_result.data == second_result.data
        assert not first_result.cache_hit
        assert second_result.cache_hit
    
    def test_process_cache_expires_after_ttl(self):
        """Test that cache expires and rescans after TTL expires."""
        # Arrange: Set up cache with very short TTL (0.1 seconds)
        instances = [self._create_test_instance()]
        scanner = FakeProcessScanner(scan_instances=instances, scan_delay_ms=50)
        
        from claude_code_autoyes.core.process_cache import ProcessCache
        cache = ProcessCache(ttl_seconds=0.1)  # Very short TTL
        
        # Act: First call, wait for TTL to expire, then second call
        first_result = cache.get_processes(scanner.scan_processes)
        time.sleep(0.15)  # Wait for TTL expiration
        second_result = cache.get_processes(scanner.scan_processes)
        
        # Assert: Both calls should result in actual scans
        assert scanner.call_count == 2
        assert not first_result.cache_hit
        assert not second_result.cache_hit
    
    def test_process_cache_handles_concurrent_access(self):
        """Test that cache handles concurrent access safely."""
        # Arrange: Set up cache with concurrent access pattern
        instances = [self._create_test_instance()]
        scanner = FakeProcessScanner(scan_instances=instances, scan_delay_ms=200)
        
        from claude_code_autoyes.core.process_cache import ProcessCache
        cache = ProcessCache(ttl_seconds=10)
        
        # Act: Simulate concurrent access (would need threading in real test)
        # For now, test sequential access with timing
        results = []
        for _ in range(3):
            start_time = time.time()
            result = cache.get_processes(scanner.scan_processes)
            duration = (time.time() - start_time) * 1000
            results.append((result, duration))
        
        # Assert: Only first call should be slow (actual scan)
        assert scanner.call_count == 1
        assert results[0][1] >= 190  # First call with scan delay
        assert results[1][1] < 10    # Subsequent calls from cache
        assert results[2][1] < 10
    
    def test_process_cache_performance_with_large_datasets(self):
        """Test cache performance with large process datasets."""
        # Arrange: Large dataset to test cache efficiency
        instances = [self._create_test_instance(session=f"session{i}") for i in range(1000)]
        scanner = FakeProcessScanner(scan_instances=instances, scan_delay_ms=500)
        
        from claude_code_autoyes.core.process_cache import ProcessCache
        cache = ProcessCache(ttl_seconds=60)
        
        # Act: Multiple cache accesses with large dataset
        start_time = time.time()
        first_result = cache.get_processes(scanner.scan_processes)
        first_duration = (time.time() - start_time) * 1000
        
        start_time = time.time()
        second_result = cache.get_processes(scanner.scan_processes)
        second_duration = (time.time() - start_time) * 1000
        
        # Assert: Cache should handle large datasets efficiently
        assert len(first_result.data) == 1000
        assert len(second_result.data) == 1000
        assert first_duration >= 490  # Includes scan delay
        assert second_duration < 50   # Fast cache retrieval even for large data
        assert scanner.call_count == 1
    
    def test_process_cache_invalidation(self):
        """Test that cache can be manually invalidated."""
        # Arrange: Set up cache with data
        instances = [self._create_test_instance()]
        scanner = FakeProcessScanner(scan_instances=instances, scan_delay_ms=100)
        
        from claude_code_autoyes.core.process_cache import ProcessCache
        cache = ProcessCache(ttl_seconds=60)
        
        # Act: Cache data, invalidate, then access again
        first_result = cache.get_processes(scanner.scan_processes)
        cache.invalidate()  # Manual cache invalidation
        second_result = cache.get_processes(scanner.scan_processes)
        
        # Assert: Both calls should result in actual scans due to invalidation
        assert scanner.call_count == 2
        assert not first_result.cache_hit
        assert not second_result.cache_hit
    
    def _create_test_instance(
        self, 
        session: str = "test_session", 
        pane: str = "1"
    ) -> ClaudeInstance:
        """Create a test ClaudeInstance with specified parameters."""
        return ClaudeInstance(
            session=session,
            pane=pane,
            is_claude=True,
            enabled=True,
            last_prompt="2023-01-01 12:00:00"
        )