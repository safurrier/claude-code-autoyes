"""Smart refresh optimization to eliminate unnecessary UI rebuilds."""

import hashlib
import time
from dataclasses import dataclass

# TYPE_CHECKING import to avoid circular imports
from typing import TYPE_CHECKING

from .models import ClaudeInstance
from .process_cache import ProcessCache

if TYPE_CHECKING:
    from .detector import ClaudeDetector


@dataclass
class RefreshResult:
    """Result of a refresh operation."""

    rebuilds_performed: int
    duration_ms: float
    changes_detected: bool
    changed_instances: list[ClaudeInstance]


class SmartRefreshOptimizer:
    """Optimizes refresh cycles by detecting changes before rebuilding UI."""

    def __init__(
        self, detector: "ClaudeDetector", process_cache: ProcessCache | None = None
    ):
        self.detector = detector
        self.process_cache = process_cache
        self._cached_fingerprint: str | None = None
        self._cached_instances: list[ClaudeInstance] = []

    def refresh_with_optimization(self) -> RefreshResult:
        """Perform optimized refresh with change detection."""
        start_time = time.time()

        # Get current instance data (using cache if available)
        if self.process_cache:
            cache_result = self.process_cache.get_processes(
                self.detector.find_claude_instances
            )
            current_instances = cache_result.data
        else:
            current_instances = self.detector.find_claude_instances()

        current_fingerprint = self.generate_fingerprint(current_instances)

        # Check if data has changed
        if self._cached_fingerprint == current_fingerprint:
            # No changes detected - skip rebuild
            duration_ms = (time.time() - start_time) * 1000
            return RefreshResult(
                rebuilds_performed=0,
                duration_ms=duration_ms,
                changes_detected=False,
                changed_instances=[],
            )

        # Changes detected - perform rebuild
        changed_instances = self._identify_changed_instances(current_instances)
        self._cached_fingerprint = current_fingerprint
        self._cached_instances = current_instances.copy()

        duration_ms = (time.time() - start_time) * 1000
        return RefreshResult(
            rebuilds_performed=1,
            duration_ms=duration_ms,
            changes_detected=True,
            changed_instances=changed_instances,
        )

    @staticmethod
    def generate_fingerprint(instances: list[ClaudeInstance]) -> str:
        """Generate a fingerprint for the instance data to detect changes."""
        # Create a stable hash of all instance data
        instance_data = []
        for instance in sorted(instances, key=lambda i: (i.session, i.pane)):
            data = f"{instance.session}:{instance.pane}:{instance.is_claude}:{instance.enabled}:{instance.last_prompt}"
            instance_data.append(data)

        combined_data = "|".join(instance_data)
        return hashlib.sha256(combined_data.encode()).hexdigest()

    def _identify_changed_instances(
        self, current_instances: list[ClaudeInstance]
    ) -> list[ClaudeInstance]:
        """Identify which specific instances have changed."""
        if not self._cached_instances:
            # First run - all instances are "new"
            return current_instances.copy()

        # For now, return all instances when changes detected
        # This can be optimized later to return only actually changed instances
        changed = []

        # Create lookup maps for comparison
        cached_map = {(i.session, i.pane): i for i in self._cached_instances}
        current_map = {(i.session, i.pane): i for i in current_instances}

        # Find changed instances
        for key, current_instance in current_map.items():
            cached_instance = cached_map.get(key)
            if not cached_instance or self._instance_changed(
                cached_instance, current_instance
            ):
                changed.append(current_instance)

        return changed

    def _instance_changed(
        self, cached: ClaudeInstance, current: ClaudeInstance
    ) -> bool:
        """Check if an instance has actually changed."""
        return (
            cached.enabled != current.enabled
            or cached.last_prompt != current.last_prompt
            or cached.is_claude != current.is_claude
        )
