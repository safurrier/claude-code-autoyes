"""Tests for incremental table updates to avoid full table rebuilds."""

import asyncio
from dataclasses import dataclass
from typing import List, Set
from unittest.mock import Mock

import pytest

from claude_code_autoyes.core.models import ClaudeInstance
from claude_code_autoyes.core.performance_constants import TABLE_UPDATE_PERFORMANCE_THRESHOLD_MS


@dataclass
class TableUpdateResult:
    """Result of a table update operation."""
    
    rows_updated: int
    rows_added: int 
    rows_removed: int
    focus_preserved: bool
    duration_ms: float


class MockDataTable:
    """Mock DataTable for testing without full TUI framework."""
    
    def __init__(self):
        self.rows = []
        self.cursor_row = 0
        self.row_count = 0
    
    def clear(self):
        self.rows = []
        self.row_count = 0
    
    def add_row(self, *args):
        self.rows.append(args)
        self.row_count += 1
    
    def add_columns(self, *args):
        pass


@pytest.mark.performance
class TestIncrementalTableUpdates:
    """Test suite for incremental table update functionality."""
    
    @pytest.mark.asyncio
    async def test_incremental_update_preserves_focus_and_scroll(self):
        """Test that incremental updates preserve user focus and scroll position."""
        # Arrange: Set up table with data and user focus
        initial_instances = [
            self._create_test_instance(session=f"session{i}") 
            for i in range(10)
        ]
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        table = MockDataTable()
        updater = IncrementalTableUpdater(table)
        
        # Act: Set initial data and focus on row 5
        await updater.update_table_data(initial_instances)
        table.cursor_row = 5
        focused_row = table.cursor_row
        
        # Update one instance (change status)
        updated_instances = initial_instances.copy()
        updated_instances[2] = self._create_test_instance(
            session="session2", enabled=False
        )
        
        result = await updater.update_table_data(updated_instances)
        
        # Assert: Focus should be preserved, only one row updated
        assert table.cursor_row == focused_row
        assert result.rows_updated == 1
        assert result.rows_added == 0
        assert result.rows_removed == 0
        assert result.focus_preserved
    
    @pytest.mark.asyncio
    async def test_incremental_update_handles_row_additions(self):
        """Test that incremental updates correctly handle new rows."""
        # Arrange: Start with small dataset, add rows
        initial_instances = [self._create_test_instance(session="session1")]
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        table = MockDataTable()
        updater = IncrementalTableUpdater(table)
        
        # Act: Set initial data, then add new instances
        await updater.update_table_data(initial_instances)
        initial_row_count = table.row_count
        
        updated_instances = initial_instances + [
            self._create_test_instance(session="session2"),
            self._create_test_instance(session="session3")
        ]
        
        result = await updater.update_table_data(updated_instances)
        
        # Assert: Two new rows should be added
        assert table.row_count == initial_row_count + 2
        assert result.rows_added == 2
        assert result.rows_updated == 0
        assert result.rows_removed == 0
    
    @pytest.mark.asyncio
    async def test_incremental_update_handles_row_removals(self):
        """Test that incremental updates correctly handle removed rows."""
        # Arrange: Start with multiple instances, remove some
        initial_instances = [
            self._create_test_instance(session=f"session{i}") 
            for i in range(5)
        ]
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        table = MockDataTable()
        updater = IncrementalTableUpdater(table)
        
        # Act: Set initial data, then remove instances
        await updater.update_table_data(initial_instances)
        initial_row_count = table.row_count
        
        # Remove middle instances (sessions 1 and 3)
        updated_instances = [
            initial_instances[0],  # session0
            initial_instances[2],  # session2  
            initial_instances[4]   # session4
        ]
        
        result = await updater.update_table_data(updated_instances)
        
        # Assert: Two rows should be removed
        assert table.row_count == initial_row_count - 2
        assert result.rows_removed == 2
        assert result.rows_added == 0
        assert result.rows_updated == 0
    
    @pytest.mark.asyncio
    async def test_incremental_update_performance_with_large_datasets(self):
        """Test that incremental updates perform well with large datasets."""
        # Arrange: Large dataset with minimal changes
        initial_instances = [
            self._create_test_instance(session=f"session{i}") 
            for i in range(1000)
        ]
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        table = MockDataTable()
        updater = IncrementalTableUpdater(table)
        
        # Act: Set initial data, then make small change
        await updater.update_table_data(initial_instances)
        
        # Change only one instance out of 1000
        updated_instances = initial_instances.copy()
        updated_instances[500] = self._create_test_instance(
            session="session500", enabled=False
        )
        
        import time
        start_time = time.time()
        result = await updater.update_table_data(updated_instances)
        duration_ms = (time.time() - start_time) * 1000
        
        # Assert: Should be fast even with large dataset
        assert duration_ms < TABLE_UPDATE_PERFORMANCE_THRESHOLD_MS, f"Update took {duration_ms}ms, should be <{TABLE_UPDATE_PERFORMANCE_THRESHOLD_MS}ms"
        assert result.rows_updated == 1
        assert result.duration_ms < TABLE_UPDATE_PERFORMANCE_THRESHOLD_MS
    
    @pytest.mark.asyncio
    async def test_incremental_update_change_detection(self):
        """Test that incremental updater correctly detects which rows changed."""
        # Arrange: Set up instances with specific changes
        initial_instances = [
            self._create_test_instance(session="session1", enabled=True),
            self._create_test_instance(session="session2", enabled=True),
            self._create_test_instance(session="session3", enabled=True)
        ]
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        table = MockDataTable()
        updater = IncrementalTableUpdater(table)
        
        # Act: Set initial data, then change specific instances
        await updater.update_table_data(initial_instances)
        
        updated_instances = [
            self._create_test_instance(session="session1", enabled=False),  # Changed
            self._create_test_instance(session="session2", enabled=True),   # Unchanged
            self._create_test_instance(session="session3", enabled=False)   # Changed
        ]
        
        result = await updater.update_table_data(updated_instances)
        
        # Assert: Should detect exactly 2 changes
        assert result.rows_updated == 2
        assert result.rows_added == 0
        assert result.rows_removed == 0
    
    def test_table_updater_row_fingerprinting(self):
        """Test that row fingerprinting correctly identifies changes."""
        # Arrange: Instances with identical vs different data
        instance1 = self._create_test_instance(session="test", enabled=True)
        instance2 = self._create_test_instance(session="test", enabled=True)
        instance3 = self._create_test_instance(session="test", enabled=False)
        
        from claude_code_autoyes.tui.components.table_updater import IncrementalTableUpdater
        
        # This should fail - generate_row_fingerprint method doesn't exist yet
        fingerprint1 = IncrementalTableUpdater.generate_row_fingerprint(instance1)
        fingerprint2 = IncrementalTableUpdater.generate_row_fingerprint(instance2)
        fingerprint3 = IncrementalTableUpdater.generate_row_fingerprint(instance3)
        
        # Assert: Identical instances have same fingerprint, different don't
        assert fingerprint1 == fingerprint2
        assert fingerprint1 != fingerprint3
    
    def _create_test_instance(
        self, 
        session: str = "test_session", 
        pane: str = "1",
        enabled: bool = True
    ) -> ClaudeInstance:
        """Create a test ClaudeInstance with specified parameters."""
        return ClaudeInstance(
            session=session,
            pane=pane,
            is_claude=True,
            enabled=enabled,
            last_prompt="2023-01-01 12:00:00"
        )