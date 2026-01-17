#!/usr/bin/env python
"""
Test runner main entry point.

Usage:
    python test/main.py                    # Run all features
    python test/main.py authentication     # Run specific feature
    python test/main.py --list             # List available features
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from test.utils.test_runner import TestRunner
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    """Main entry point for test runner."""
    # Parse command line arguments
    feature = None
    list_features = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--list" or sys.argv[1] == "-l":
            list_features = True
        elif not sys.argv[1].startswith("-"):
            feature = sys.argv[1]
        else:
            console.print(
                Panel.fit(
                    "[bold red]Invalid argument[/bold red]\n\n"
                    "Usage:\n"
                    "  python test/main.py                    # Run all features\n"
                    "  python test/main.py authentication     # Run specific feature\n"
                    "  python test/main.py --list             # List available features",
                    border_style="red",
                )
            )
            sys.exit(1)

    runner = TestRunner()

    if list_features:
        features = runner.discover_features()
        if features:
            features_list = "\n".join(f"  • {f}" for f in features)
            console.print(
                Panel.fit(
                    "[bold]Available features:[/bold]\n\n" + features_list,
                    border_style="blue",
                    title="Features",
                )
            )
        else:
            console.print(
                Panel.fit(
                    "[bold yellow]No features found[/bold yellow]",
                    border_style="yellow",
                )
            )
        return

    async def run_tests() -> None:
        """Async wrapper for running tests."""
        if feature:
            # Run specific feature
            await runner.run_feature(feature)
        else:
            # Run all features
            await runner.run_all_features()

    # Run async test function
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Tests interrupted by user[/bold yellow]")
        sys.exit(130)
    except SystemExit as e:
        sys.exit(e.code if e.code else 1)
    except Exception as e:
        console.print(
            Panel.fit(
                f"[bold red]Unexpected error[/bold red]\n\n{str(e)}", border_style="red"
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
