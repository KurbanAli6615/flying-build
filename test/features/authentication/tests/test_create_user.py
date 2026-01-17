"""
Test file for POST /user API endpoint (user creation).
"""
from rich.console import Console

from test.features.authentication import helpers as auth_helpers
from test.utils.validators import (
    assert_response_contains,
    validate_json_response,
    validate_status_code,
)

console = Console()


async def test_create_user_1(test_instance) -> None:
    """
    Test creating test user 1 via POST /user endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_1_data
    """
    console.print("[yellow]Test: Create Test User 1[/yellow]")

    encrypted_payload = await auth_helpers.prepare_user_creation_payload(
        test_instance.user_1_data,
        test_instance.api_client,
        test_instance.encryption_helper,
    )

    response = await test_instance.api_client.post("/user", json=encrypted_payload)
    # Only check HTTP status code - 200-299 is success
    validate_status_code(response, 201)

    # Validate response structure (no need to check status field - we only rely on HTTP status code)
    response_data = validate_json_response(response)
    assert_response_contains(response_data, "data.message", str, api_client=test_instance.api_client)

    console.print("  [green]✓ User 1 created successfully[/green]")


async def test_create_user_2(test_instance) -> None:
    """
    Test creating test user 2 via POST /user endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_2_data
    """
    console.print("[yellow]Test: Create Test User 2[/yellow]")

    encrypted_payload = await auth_helpers.prepare_user_creation_payload(
        test_instance.user_2_data,
        test_instance.api_client,
        test_instance.encryption_helper,
    )

    response = await test_instance.api_client.post("/user", json=encrypted_payload)
    # Only check HTTP status code - 200-299 is success
    validate_status_code(response, 201)

    # Validate response structure (no need to check status field - we only rely on HTTP status code)
    response_data = validate_json_response(response)
    assert_response_contains(response_data, "data.message", str, api_client=test_instance.api_client)

    console.print("  [green]✓ User 2 created successfully[/green]")
