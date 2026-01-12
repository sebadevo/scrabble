"""Scrabble package entrypoint.

Exposes the console script entrypoint used by the `scrabble` command.
"""

from scrabble.main import run


def main() -> None:
    """Run the Scrabble game CLI."""
    run()
