"""Tests for smart refresh optimization to eliminate unnecessary UI rebuilds."""

import time
from dataclasses import dataclass
from typing import List

import pytest

from claude_code_autoyes.core.models import ClaudeInstance
from claude_code_autoyes.core.performance_constants import (
    REFRESH_PERFORMANCE_THRESHOLD_MS,
    SKIP_REFRESH_THRESHOLD_MS,
)


@dataclass
class RefreshResult:
    """Result of a refresh operation."""
    
    rebuilds_performed: int
    duration_ms: float
    changes_detected: bool
    changed_instances: List[ClaudeInstance]


class FakeClaudeDetector:
    """Test double for ClaudeDetector with controllable instance data."""
    
    def __init__(self, fixed_instances: List[ClaudeInstance]):
        self.instances = fixed_instances
        self.call_count = 0
    
    def find_claude_instances(self) -> List[ClaudeInstance]:
        """Return the fixed instances, tracking call count."""
        self.call_count += 1
        return self.instances.copy()


@pytest.mark.performance
class TestSmartRefreshOptimization:
    """Test suite for smart refresh optimization functionality."""
    
    def test_smart_refresh_skips_rebuild_when_data_unchanged(self):
        """Test that refresh cycles detect unchanged data and skip expensive rebuilds."""
        # Arrange: Set up stable instance data with change detector
        instances = [self._create_test_instance()]
        detector = FakeClaudeDetector(fixed_instances=instances)
        
        # This should fail - SmartRefreshOptimizer doesn't exist yet
        from claude_code_autoyes.core.refresh_optimizer import SmartRefreshOptimizer
        optimizer = SmartRefreshOptimizer(detector)
        
        # Act: Perform first refresh (should rebuild), then second (should skip)
        first_refresh = optimizer.refresh_with_optimization()
        second_refresh = optimizer.refresh_with_optimization()
        
        # Assert: Second refresh should be optimized skip
        assert first_refresh.rebuilds_performed == 1
        assert second_refresh.rebuilds_performed == 0
        assert second_refresh.duration_ms < SKIP_REFRESH_THRESHOLD_MS
        assert not second_refresh.changes_detected
    
    def test_smart_refresh_detects_instance_changes(self):
        """Test that refresh cycles detect when instance data actually changes."""
        # Arrange: Set up detector with changeable instance data
        initial_instances = [self._create_test_instance(session="session1")]
        detector = FakeClaudeDetector(fixed_instances=initial_instances)
        
        from claude_code_autoyes.core.refresh_optimizer import SmartRefreshOptimizer
        optimizer = SmartRefreshOptimizer(detector)
        
        # Act: First refresh, then change data, then second refresh
        first_refresh = optimizer.refresh_with_optimization()
        
        # Change the instance data
        changed_instances = [self._create_test_instance(session="session2")]
        detector.instances = changed_instances
        
        second_refresh = optimizer.refresh_with_optimization()
        
        # Assert: Second refresh should detect changes and rebuild
        assert first_refresh.rebuilds_performed == 1
        assert second_refresh.rebuilds_performed == 1
        assert second_refresh.changes_detected
        assert len(second_refresh.changed_instances) == 1
    
    def test_smart_refresh_performance_baseline(self):
        """Test that optimized refresh cycles complete within performance thresholds."""
        # Arrange: Large dataset to test performance
        instances = [self._create_test_instance(session=f"session{i}") for i in range(100)]
        detector = FakeClaudeDetector(fixed_instances=instances)
        
        from claude_code_autoyes.core.refresh_optimizer import SmartRefreshOptimizer
        optimizer = SmartRefreshOptimizer(detector)
        
        # Act: Measure performance of optimized refresh
        start_time = time.time()
        refresh_result = optimizer.refresh_with_optimization()
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert: Should complete within reasonable time
        assert duration_ms < REFRESH_PERFORMANCE_THRESHOLD_MS, f"Refresh took {duration_ms}ms, should be <{REFRESH_PERFORMANCE_THRESHOLD_MS}ms"
        assert refresh_result.duration_ms < REFRESH_PERFORMANCE_THRESHOLD_MS, f"Internal duration {refresh_result.duration_ms}ms should be <{REFRESH_PERFORMANCE_THRESHOLD_MS}ms"
    
    def test_smart_refresh_fingerprint_comparison(self):
        """Test that instance fingerprinting correctly identifies changes."""
        # Arrange: Two instances that are identical vs different
        instance1 = self._create_test_instance(session="test", pane="1", enabled=True)
        instance2 = self._create_test_instance(session="test", pane="1", enabled=True)
        instance3 = self._create_test_instance(session="test", pane="1", enabled=False)
        
        from claude_code_autoyes.core.refresh_optimizer import SmartRefreshOptimizer
        
        # This should fail - generate_fingerprint method doesn't exist yet
        fingerprint1 = SmartRefreshOptimizer.generate_fingerprint([instance1])
        fingerprint2 = SmartRefreshOptimizer.generate_fingerprint([instance2])
        fingerprint3 = SmartRefreshOptimizer.generate_fingerprint([instance3])
        
        # Assert: Identical instances have same fingerprint, different instances don't
        assert fingerprint1 == fingerprint2
        assert fingerprint1 != fingerprint3
    
    def _create_test_instance(
        self, 
        session: str = "test_session", 
        pane: str = "1", 
        enabled: bool = True,
        is_claude: bool = True
    ) -> ClaudeInstance:
        """Create a test ClaudeInstance with specified parameters."""
        return ClaudeInstance(
            session=session,
            pane=pane,
            is_claude=is_claude,
            enabled=enabled,
            last_prompt="2023-01-01 12:00:00"
        )