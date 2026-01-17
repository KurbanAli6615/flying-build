from rich.console import Console

from test.base.base_test import BaseTestFeature
from test.features.authentication.tests import (
    test_create_user,
    test_get_self,
    test_public_key,
    test_sign_in,
)
from test.utils.encryption import EncryptionHelper
from test.utils.test_users import TestUserManager

console = Console()


class AuthenticationTests(BaseTestFeature):
    """
    Authentication feature tests.

    Tests all authentication-related API endpoints:
    - Get public key
    - Create user
    - Sign in
    - Get self (authenticated)
    """

    feature_name = "authentication"

    def __init__(self, api_client, config) -> None:
        """Initialize authentication tests."""
        super().__init__(api_client, config)
        self.encryption_helper = EncryptionHelper()
        self.user_1_data = None
        self.user_2_data = None
        self.user_1_tokens = None
        self.user_2_tokens = None

    async def setup(self) -> None:
        """Setup before running tests."""
        console.print("[bold blue]Setting up authentication tests...[/bold blue]")

        # Get test user data from config (this will print user info automatically)
        self.user_1_data = TestUserManager.get_test_user_1(self.config)
        self.user_2_data = TestUserManager.get_test_user_2(self.config)

    async def run_tests(self) -> None:
        """Run all authentication tests."""
        console.print("[bold green]Starting authentication tests...[/bold green]\n")

        # Test: Get Public Key
        await test_public_key.test_get_public_key(self)

        # Test: Create Test User 1
        await test_create_user.test_create_user_1(self)

        # Test: Create Test User 2
        await test_create_user.test_create_user_2(self)

        # Test: Sign In User 1
        await test_sign_in.test_sign_in_user_1(self)

        # Test: Sign In User 2
        await test_sign_in.test_sign_in_user_2(self)

        # Test: Get Self (User 1)
        await test_get_self.test_get_self_user_1(self)

        # Test: Get Self (User 2)
        await test_get_self.test_get_self_user_2(self)

        console.print("\n[bold green]✓ All authentication tests passed![/bold green]")

    async def teardown(self) -> None:
        """Cleanup after tests."""
        console.print("[bold blue]Cleaning up authentication tests...[/bold blue]")
        # Clear cookies
        self.api_client.clear_cookies()
        # Clear encryption cache
        self.encryption_helper.clear_cache()
