"""
Test file for POST /user/sign-in API endpoint.
"""

from test.features.authentication import helpers as auth_helpers
from test.utils.validators import (
    assert_response_contains,
    validate_json_response,
    validate_status_code,
)

from rich.console import Console

console = Console()


async def test_sign_in_user_1(test_instance) -> None:
    """
    Test signing in with user 1 via POST /user/sign-in endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_1_data
    """
    console.print("[yellow]Test: Sign In User 1[/yellow]")

    encrypted_payload = await auth_helpers.prepare_signin_payload(
        test_instance.user_1_data["email"],
        test_instance.user_1_data["password"],
        test_instance.api_client,
        test_instance.encryption_helper,
    )

    response = await test_instance.api_client.post(
        "/user/sign-in", json=encrypted_payload
    )
    # Only check HTTP status code - 200-299 is success
    validate_status_code(response, 200)

    # Validate response structure (no need to check status/code fields - we only rely on HTTP status code)
    # Note: API returns snake_case: access_token, refresh_token (not camelCase)
    response_data = validate_json_response(response)
    assert_response_contains(
        response_data, "data.access_token", str, api_client=test_instance.api_client
    )
    assert_response_contains(
        response_data, "data.refresh_token", str, api_client=test_instance.api_client
    )

    # Extract and store tokens
    test_instance.user_1_tokens = auth_helpers.extract_auth_tokens(response_data)

    # Set cookies for authenticated requests
    cookies = response.cookies
    if cookies:
        test_instance.api_client.set_cookies(dict(cookies))

    console.print("  [green]✓ User 1 signed in successfully[/green]")


async def test_sign_in_user_2(test_instance) -> None:
    """
    Test signing in with user 2 via POST /user/sign-in endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_2_data
    """
    console.print("[yellow]Test: Sign In User 2[/yellow]")

    encrypted_payload = await auth_helpers.prepare_signin_payload(
        test_instance.user_2_data["email"],
        test_instance.user_2_data["password"],
        test_instance.api_client,
        test_instance.encryption_helper,
    )

    response = await test_instance.api_client.post(
        "/user/sign-in", json=encrypted_payload
    )
    validate_status_code(response, 200)

    # Validate response structure (no need to check status/code fields - we only rely on HTTP status code)
    # Note: API returns snake_case: access_token, refresh_token (not camelCase)
    response_data = validate_json_response(response)
    assert_response_contains(
        response_data, "data.access_token", str, api_client=test_instance.api_client
    )
    assert_response_contains(
        response_data, "data.refresh_token", str, api_client=test_instance.api_client
    )

    # Extract and store tokens
    test_instance.user_2_tokens = auth_helpers.extract_auth_tokens(response_data)

    # Set cookies for authenticated requests
    cookies = response.cookies
    if cookies:
        test_instance.api_client.set_cookies(dict(cookies))

    console.print("  [green]✓ User 2 signed in successfully[/green]")
