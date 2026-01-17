import os
import sys
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config import settings
from rich.console import Console

console = Console()


class TestConfig:
    """
    Test configuration management.

    Reads base URL from:
    1. Environment variable TEST_BASE_URL
    2. Config file (future enhancement)
    3. Default to http://localhost:{APP_PORT} from settings
    """

    _instance: Optional["TestConfig"] = None
    _base_url: Optional[str] = None

    def __new__(cls) -> "TestConfig":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize test configuration."""
        if self._base_url is None:
            self._base_url = self._load_base_url()
        # Initialize instance variable for caching test users
        self._cached_users: Optional[tuple[dict, dict]] = None

    def _load_base_url(self) -> str:
        """
        Load base URL from environment variable or use default.

        Returns:
            str: Base URL for API testing
        """
        # Check environment variable first
        test_base_url = os.getenv("TEST_BASE_URL")
        if test_base_url:
            return test_base_url.rstrip("/")

        # Default to localhost with port from settings
        host = settings.APP_HOST or "localhost"
        port = settings.APP_PORT or 8000
        return f"http://{host}:{port}"

    def get_base_url(self) -> str:
        """
        Get the base URL for API testing.

        Returns:
            str: Base URL
        """
        return self._base_url

    def get_test_users(self) -> tuple[dict, dict]:
        """
        Get predefined test user credentials.

        These users should not exist in the existing database.
        Users are cached after first generation to ensure consistency.

        Returns:
            tuple[dict, dict]: Two test user dictionaries with credentials
        """
        # Return cached users if they exist
        if self._cached_users is not None:
            return self._cached_users

        # Generate unique test users that won't conflict with existing data
        import uuid
        import random

        unique_suffix = str(uuid.uuid4())[:8]
        # Generate numeric-only suffixes for phone numbers (unique for each user)
        phone_suffix_1 = "".join([str(random.randint(0, 9)) for _ in range(4)])
        phone_suffix_2 = "".join([str(random.randint(0, 9)) for _ in range(4)])

        test_user_1 = {
            "name": "Test User One",
            "username": f"testuser1_{unique_suffix}",
            "email": f"testuser1_{unique_suffix}@test.com",
            "country_code": "+1",
            "phone": f"123456{phone_suffix_1}",
            "password": "TestPassword123!@#",
        }

        test_user_2 = {
            "name": "Test User Two",
            "username": f"testuser2_{unique_suffix}",
            "email": f"testuser2_{unique_suffix}@test.com",
            "country_code": "+1",
            "phone": f"987654{phone_suffix_2}",
            "password": "TestPassword456!@#",
        }

        # Print user information for tracking in DB
        console.print(
            "\n[bold yellow]📋 Test User Information (for DB tracking):[/bold yellow]"
        )
        console.print("\n[cyan]User 1:[/cyan]")
        console.print(f"  Name: {test_user_1['name']}")
        console.print(f"  Username: {test_user_1['username']}")
        console.print(f"  Email: {test_user_1['email']}")
        console.print(f"  Country Code: {test_user_1['country_code']}")
        console.print(f"  Phone: {test_user_1['phone']}")
        console.print(f"  Password: {test_user_1['password']}")
        console.print("\n[cyan]User 2:[/cyan]")
        console.print(f"  Name: {test_user_2['name']}")
        console.print(f"  Username: {test_user_2['username']}")
        console.print(f"  Email: {test_user_2['email']}")
        console.print(f"  Country Code: {test_user_2['country_code']}")
        console.print(f"  Phone: {test_user_2['phone']}")
        console.print(f"  Password: {test_user_2['password']}")
        console.print("")

        # Cache the users
        self._cached_users = (test_user_1, test_user_2)

        return test_user_1, test_user_2


# Global instance
test_config = TestConfig()
