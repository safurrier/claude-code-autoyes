"""Process detection caching to reduce filesystem scanning overhead."""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from .models import ClaudeInstance
from .performance_constants import DEFAULT_PROCESS_CACHE_TTL_SECONDS


@dataclass
class CacheResult:
    """Result of a cache operation."""

    cache_hit: bool
    duration_ms: float
    data: list[ClaudeInstance]


class ProcessCache:
    """Caches process detection results with TTL to reduce scanning overhead."""

    def __init__(self, ttl_seconds: int = DEFAULT_PROCESS_CACHE_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._cached_data: list[ClaudeInstance] | None = None
        self._cache_timestamp: float | None = None
        self._lock = threading.Lock()

    def get_processes(
        self, scanner_func: Callable[[], list[ClaudeInstance]]
    ) -> CacheResult:
        """Get processes from cache or scan if expired/empty."""
        start_time = time.time()

        with self._lock:
            current_time = time.time()

            # Check if cache is valid
            if (
                self._cached_data is not None
                and self._cache_timestamp is not None
                and (current_time - self._cache_timestamp) < self.ttl_seconds
            ):
                # Cache hit
                duration_ms = (time.time() - start_time) * 1000
                return CacheResult(
                    cache_hit=True,
                    duration_ms=duration_ms,
                    data=self._cached_data.copy(),
                )

            # Cache miss - scan for new data
            self._cached_data = scanner_func()
            self._cache_timestamp = current_time

            duration_ms = (time.time() - start_time) * 1000
            return CacheResult(
                cache_hit=False, duration_ms=duration_ms, data=self._cached_data.copy()
            )

    def invalidate(self) -> None:
        """Manually invalidate the cache."""
        with self._lock:
            self._cached_data = None
            self._cache_timestamp = None
