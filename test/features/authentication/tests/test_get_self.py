"""
Test file for GET /user/self API endpoint.
"""
from rich.console import Console

from test.features.authentication import helpers as auth_helpers
from test.utils.validators import (
    assert_response_contains,
    validate_json_response,
    validate_status_code,
)

console = Console()


async def test_get_self_user_1(test_instance) -> None:
    """
    Test getting self data for user 1 via GET /user/self endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_1_data
    """
    console.print("[yellow]Test: Get Self (User 1)[/yellow]")

    # Sign in again to get fresh cookies for user 1
    encrypted_payload = await auth_helpers.prepare_signin_payload(
        test_instance.user_1_data["email"],
        test_instance.user_1_data["password"],
        test_instance.api_client,
        test_instance.encryption_helper,
    )

    response = await test_instance.api_client.post(
        "/user/sign-in", json=encrypted_payload
    )
    validate_status_code(response, 200)

    # Now get self
    response = await test_instance.api_client.get("/user/self")
    # Only check HTTP status code - 200-299 is success
    validate_status_code(response, 200)

    # Validate response structure (no need to check status/code fields - we only rely on HTTP status code)
    # BaseUserResponse uses camelCase (countryCode, not country_code) due to CamelCaseModel
    response_data = validate_json_response(response)
    assert_response_contains(response_data, "data.id", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.email", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.name", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.username", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.countryCode", str, api_client=test_instance.api_client)  # camelCase from BaseUserResponse
    assert_response_contains(response_data, "data.phone", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.role", str, api_client=test_instance.api_client)

    # Validate user data matches
    user_data = auth_helpers.extract_user_data(response_data)
    if user_data.get("email") != test_instance.user_1_data["email"]:
        raise ValueError(
            f"Email mismatch: expected {test_instance.user_1_data['email']}, got {user_data.get('email')}"
        )

    console.print("  [green]✓ User 1 self data retrieved successfully[/green]")


async def test_get_self_user_2(test_instance) -> None:
    """
    Test getting self data for user 2 via GET /user/self endpoint.

    Args:
        test_instance: AuthenticationTests instance with api_client, encryption_helper, and user_2_data
    """
    console.print("[yellow]Test: Get Self (User 2)[/yellow]")

    # Sign in again to get fresh cookies for user 2
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

    # Now get self
    response = await test_instance.api_client.get("/user/self")
    # Only check HTTP status code - 200-299 is success
    validate_status_code(response, 200)

    # Validate response structure (no need to check status/code fields - we only rely on HTTP status code)
    # BaseUserResponse uses camelCase (countryCode, not country_code) due to CamelCaseModel
    response_data = validate_json_response(response)
    assert_response_contains(response_data, "data.id", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.email", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.name", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.username", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.countryCode", str, api_client=test_instance.api_client)  # camelCase from BaseUserResponse
    assert_response_contains(response_data, "data.phone", str, api_client=test_instance.api_client)
    assert_response_contains(response_data, "data.role", str, api_client=test_instance.api_client)

    # Validate user data matches
    user_data = auth_helpers.extract_user_data(response_data)
    if user_data.get("email") != test_instance.user_2_data["email"]:
        raise ValueError(
            f"Email mismatch: expected {test_instance.user_2_data['email']}, got {user_data.get('email')}"
        )

    console.print("  [green]✓ User 2 self data retrieved successfully[/green]")
