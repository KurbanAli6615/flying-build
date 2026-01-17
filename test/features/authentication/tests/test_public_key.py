"""
Test file for GET /user/public-key API endpoint.
"""
from rich.console import Console

from test.utils.validators import validate_status_code

console = Console()


async def test_get_public_key(test_instance) -> None:
    """
    Test getting public key from GET /user/public-key endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client and encryption_helper
    """
    console.print("[yellow]Test: Get Public Key[/yellow]")

    response = await test_instance.api_client.get("/user/public-key")
    # Only check status code - if it's 200, the endpoint is working
    validate_status_code(response, 200)

    console.print("  [green]✓ Public key retrieved successfully[/green]")
