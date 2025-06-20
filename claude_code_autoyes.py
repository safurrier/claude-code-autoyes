#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.7",
#     "textual>=0.89.0"
# ]
# ///

"""UV script wrapper for claude-code-autoyes."""

import sys
from pathlib import Path

# Add the project root to Python path for development
sys.path.insert(0, str(Path(__file__).parent))

from claude_code_autoyes.cli import cli

if __name__ == "__main__":
    cli()