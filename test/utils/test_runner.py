import importlib
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from test.base.base_test import BaseTestFeature
from test.configuration.config import TestConfig, test_config
from test.utils.api_client import APIClient

console = Console()

# Get the test directory path
TEST_DIR = Path(__file__).parent.parent
FEATURES_DIR = TEST_DIR / "features"


class TestRunner:
    """
    Discovers and runs feature tests.

    Automatically discovers test features in the test/features directory
    and provides methods to run them individually or all together.
    """

    def __init__(self) -> None:
        """Initialize the test runner."""
        self.config = test_config
        self.features_cache: dict[str, type[BaseTestFeature]] = {}

    def discover_features(self) -> list[str]:
        """
        Discover all available test features.

        Returns:
            list[str]: List of feature names
        """
        features = []

        if not FEATURES_DIR.exists():
            return features

        # Iterate through feature directories
        for feature_dir in FEATURES_DIR.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith("_"):
                continue

            # Check if there's a test file
            test_file = feature_dir / f"test_{feature_dir.name}.py"
            if test_file.exists():
                features.append(feature_dir.name)

        return sorted(features)

    def get_feature_class(self, feature_name: str) -> Optional[type[BaseTestFeature]]:
        """
        Get the test class for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            Optional[type[BaseTestFeature]]: Feature test class or None if not found
        """
        # Check cache first
        if feature_name in self.features_cache:
            return self.features_cache[feature_name]

        # Check if feature directory exists
        feature_dir = FEATURES_DIR / feature_name
        if not feature_dir.exists():
            return None

        # Check if test file exists
        test_file = feature_dir / f"test_{feature_name}.py"
        if not test_file.exists():
            return None

        # Import the module
        try:
            module_path = f"test.features.{feature_name}.test_{feature_name}"
            module = importlib.import_module(module_path)

            # Find the test class (should inherit from BaseTestFeature)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseTestFeature)
                    and attr != BaseTestFeature
                ):
                    self.features_cache[feature_name] = attr
                    return attr

        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Failed to load feature '{feature_name}'[/bold red]\n\nError: {str(e)}",
                    border_style="red",
                    title="Import Error",
                )
            )
            return None

        return None

    async def run_feature(self, feature_name: str) -> bool:
        """
        Run tests for a specific feature.

        Args:
            feature_name: Name of the feature to run

        Returns:
            bool: True if all tests passed, False otherwise
        """
        # Get feature class
        feature_class = self.get_feature_class(feature_name)
        if not feature_class:
            console.print(
                Panel(
                    f"[bold red]Feature '{feature_name}' not found[/bold red]",
                    border_style="red",
                    title="Error",
                )
            )
            return False

        # Initialize API client
        base_url = self.config.get_base_url()

        console.print(
            Panel(
                f"[bold green]Running feature: {feature_name}[/bold green]\nBase URL: {base_url}",
                border_style="green",
                title="Test Execution",
            )
        )

        try:
            async with APIClient(base_url) as api_client:
                # Create feature test instance
                feature_test = feature_class(api_client, self.config)

                # Run setup
                await feature_test.setup()

                # Run tests
                await feature_test.run_tests()

                # Run teardown
                await feature_test.teardown()

            console.print(
                Panel(
                    f"[bold green]✓ Feature '{feature_name}' passed[/bold green]",
                    border_style="green",
                    title="Success",
                )
            )
            return True

        except SystemExit:
            # SystemExit is used by APIClient to stop on errors
            # Let it propagate to stop execution
            console.print(
                Panel(
                    f"[bold red]✗ Feature '{feature_name}' failed[/bold red]",
                    border_style="red",
                    title="Failure",
                )
            )
            raise
        except Exception as e:
            # Format error message to preserve newlines and formatting
            error_msg = str(e)
            # If error message contains curl command, format it nicely
            if "Curl Command:" in error_msg:
                # Split error message to highlight curl command
                parts = error_msg.split("Curl Command:", 1)
                if len(parts) == 2:
                    error_msg = f"{parts[0]}\n[bold yellow]Curl Command:[/bold yellow]\n{parts[1]}"
            
            console.print(
                Panel(
                    f"[bold red]✗ Feature '{feature_name}' failed with exception[/bold red]\n\n{error_msg}",
                    border_style="red",
                    title="Error",
                )
            )
            return False

    async def run_all_features(self) -> dict[str, bool]:
        """
        Run all discovered features.

        Returns:
            dict[str, bool]: Dictionary mapping feature names to success status
        """
        features = self.discover_features()

        if not features:
            console.print(
                Panel(
                    "[bold yellow]No features found[/bold yellow]",
                    border_style="yellow",
                    title="Warning",
                )
            )
            return {}

        console.print(
            Panel(
                f"[bold]Found {len(features)} feature(s): {', '.join(features)}[/bold]",
                border_style="blue",
                title="Features Discovered",
            )
        )

        results: dict[str, bool] = {}

        for feature_name in features:
            results[feature_name] = await self.run_feature(feature_name)

        # Print summary
        passed = sum(1 for v in results.values() if v)
        total = len(results)

        if passed == total:
            console.print(
                Panel(
                    f"[bold green]All {total} feature(s) passed[/bold green]",
                    border_style="green",
                    title="Summary",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]{passed}/{total} feature(s) passed[/bold red]",
                    border_style="red",
                    title="Summary",
                )
            )
            sys.exit(1)

        return results
