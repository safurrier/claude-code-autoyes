"""Debug performance analysis CLI commands."""

import os
import subprocess
import tempfile
from dataclasses import dataclass

import click

# Import ProfileWorkflow from performance module


@dataclass
class ProfileResult:
    """Result of a profiling operation."""

    success: bool
    error: str | None = None
    output_path: str | None = None


@dataclass
class NavigationBenchmark:
    """Results from navigation performance benchmark."""

    average_response_time: float
    max_response_time: float
    action_times: dict[str, float]


class DebugCommands:
    """Performance debugging command implementations."""

    def measure_startup_time(self) -> float:
        """Measure TUI startup time."""
        # Import here to avoid circular imports during startup measurement
        from claude_code_autoyes.core.performance import StartupTimer

        timer = StartupTimer()
        return timer.measure_tui_startup()

    def check_pyspy_available(self) -> bool:
        """Check if py-spy is available on the system."""
        try:
            result = subprocess.run(
                ["py-spy", "--version"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_pyspy_install_help(self) -> str:
        """Get installation help for py-spy."""
        return (
            "py-spy is not installed. Install with:\n"
            "  pip install py-spy\n"
            "or\n"
            "  cargo install py-spy"
        )

    def profile_tui(
        self, duration: int = 30, output_path: str | None = None
    ) -> ProfileResult:
        """Profile the TUI application using py-spy."""
        if not self.check_pyspy_available():
            return ProfileResult(
                success=False,
                error="py-spy not available. " + self.get_pyspy_install_help(),
            )

        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(), "claude-autoyes-profile.svg"
            )

        try:
            # Find running TUI process
            ps_result = subprocess.run(
                ["pgrep", "-f", "claude_code_autoyes.*tui"],
                capture_output=True,
                text=True,
            )

            if ps_result.returncode != 0 or not ps_result.stdout.strip():
                return ProfileResult(
                    success=False,
                    error="No running TUI process found. Start TUI first.",
                )

            pid = ps_result.stdout.strip().split("\n")[0]

            # Run py-spy profiling
            result = subprocess.run(
                ["py-spy", "record", "-p", pid, "-d", str(duration), "-o", output_path],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return ProfileResult(
                    success=False, error=f"py-spy failed: {result.stderr}"
                )

            return ProfileResult(success=True, output_path=output_path)

        except Exception as e:
            return ProfileResult(success=False, error=f"Profiling failed: {str(e)}")

    def run_navigation_benchmark(self) -> NavigationBenchmark:
        """Run navigation performance benchmark."""
        # Import here to avoid circular imports
        from claude_code_autoyes.core.performance import NavigationTimer

        nav_timer = NavigationTimer()
        action_times = nav_timer.measure_navigation_actions(
            ["arrow_down", "arrow_up", "enter", "space", "tab"]
        )

        times = list(action_times.values())
        return NavigationBenchmark(
            average_response_time=sum(times) / len(times),
            max_response_time=max(times),
            action_times=action_times,
        )


@click.group()
def debug() -> None:
    """Performance debugging and analysis commands."""
    pass


@debug.command()
@click.option(
    "--duration", "-d", default=30, type=int, help="Profiling duration in seconds"
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Output file path for flame graph",
)
def profile(duration: int, output: str | None) -> None:
    """Profile running TUI with py-spy and generate flame graph."""
    debug_cmd = DebugCommands()

    if not debug_cmd.check_pyspy_available():
        click.echo("❌ py-spy not available")
        click.echo(debug_cmd.get_pyspy_install_help())
        return

    click.echo(f"🔥 Profiling TUI for {duration} seconds...")

    result = debug_cmd.profile_tui(duration=duration, output_path=output)

    if result.success:
        click.echo(f"✅ Profile complete: {result.output_path}")
        click.echo(f"🔍 Open {result.output_path} in a browser to view flame graph")
    else:
        click.echo(f"❌ Profiling failed: {result.error}")


@debug.command(name="startup-time")
def startup_time() -> None:
    """Measure TUI startup time."""
    debug_cmd = DebugCommands()

    click.echo("⏱️  Measuring startup time...")
    startup_time_ms = debug_cmd.measure_startup_time()

    click.echo(f"🚀 Startup time: {startup_time_ms:.3f}s")

    if startup_time_ms < 0.5:
        click.echo("✅ Excellent startup performance")
    elif startup_time_ms < 1.0:
        click.echo("✅ Good startup performance")
    elif startup_time_ms < 2.0:
        click.echo("⚠️  Startup time could be improved")
    else:
        click.echo("❌ Slow startup - investigate bottlenecks")


@debug.command(name="navigation-test")
def navigation_test() -> None:
    """Test navigation performance and responsiveness."""
    debug_cmd = DebugCommands()

    click.echo("⌨️  Running navigation benchmark...")

    try:
        results = debug_cmd.run_navigation_benchmark()

        click.echo("📊 Navigation Performance Results:")
        click.echo(f"  Average response time: {results.average_response_time:.3f}s")
        click.echo(f"  Max response time: {results.max_response_time:.3f}s")

        click.echo("📋 Individual action times:")
        for action, time_ms in results.action_times.items():
            status = "✅" if time_ms < 0.1 else "⚠️" if time_ms < 0.2 else "❌"
            click.echo(f"  {action}: {time_ms:.3f}s {status}")

        if results.average_response_time < 0.1:
            click.echo("✅ Excellent navigation performance")
        elif results.average_response_time < 0.2:
            click.echo("✅ Good navigation performance")
        else:
            click.echo("❌ Navigation performance needs improvement")

    except Exception as e:
        click.echo(f"❌ Navigation test failed: {str(e)}")
