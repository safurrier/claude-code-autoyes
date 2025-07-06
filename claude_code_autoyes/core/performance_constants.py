"""Performance optimization constants and configuration."""

# Process Cache Configuration
DEFAULT_PROCESS_CACHE_TTL_SECONDS = 10
"""Default TTL for process detection cache in seconds.

Balances responsiveness with performance:
- 10 seconds provides good responsiveness for typical usage
- Reduces expensive process scanning operations
- Can be adjusted based on user needs
"""

# Smart Refresh Optimization
REFRESH_PERFORMANCE_THRESHOLD_MS = 500
"""Maximum acceptable refresh duration in milliseconds.

Performance baseline targets:
- Regular refresh cycles should complete within 500ms
- Optimized skips should be under 100ms
- Large datasets (100+ instances) should stay under this threshold
"""

SKIP_REFRESH_THRESHOLD_MS = 100
"""Target for optimized refresh skips in milliseconds.

When no changes are detected, refresh operations should
complete very quickly to maintain UI responsiveness.
"""

# Incremental Table Updates
TABLE_UPDATE_PERFORMANCE_THRESHOLD_MS = 100
"""Maximum acceptable table update duration in milliseconds.

For incremental table updates with large datasets:
- Updates should be fast even with 1000+ rows
- Only changed rows should be processed
- Focus and scroll position should be preserved
"""

# Debug and Monitoring
DEBUG_NOTIFICATION_TIMEOUT_SECONDS = 2
"""Timeout for debug mode performance notifications."""

PERFORMANCE_MEASUREMENT_ITERATIONS = 3
"""Number of iterations for performance baseline measurements."""

# TUI Performance
TUI_STARTUP_BASELINE_MS = 1000
"""Expected TUI startup time in milliseconds.

Current baseline: ~730ms
Target: Keep under 1000ms for good user experience
"""

TUI_NAVIGATION_BASELINE_MS = 100
"""Expected navigation response time in milliseconds.

Current baseline: ~56ms
Target: Keep under 100ms for responsive feel
"""

# Cache and Memory
MAX_CACHED_INSTANCES = 10000
"""Maximum number of instances to cache in memory.

Prevents unbounded memory growth while supporting
large tmux environments with many panes.
"""

FINGERPRINT_CACHE_SIZE = 1000
"""Maximum number of fingerprints to cache for change detection."""
