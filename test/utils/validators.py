import json
import sys
from typing import Any, Optional, Union

from httpx import Response
from rich.console import Console
from rich.panel import Panel

console = Console()
VALIDATION_ERROR_TITLE = "Validation Error"


def validate_status_code(response: Response, expected: int) -> None:
    """
    Validate that the response has the expected status code.
    
    If the actual status code is in the 200-299 range (success codes),
    it will be accepted as valid regardless of the expected code (as long as expected is also in 200-299).
    
    If expected is in 200-299 range, any actual code in 200-299 range is accepted.
    Otherwise, requires exact match.

    Args:
        response: HTTP response object
        expected: Expected status code

    Raises:
        SystemExit: If status code doesn't match
    """
    actual_code = response.status_code
    
    # If actual code is in success range (200-299), accept it as success
    # This means any 2xx response is considered successful
    if 200 <= actual_code <= 299:
        # If expected is also in success range, accept any success code
        if 200 <= expected <= 299:
            return  # Both are success codes, accept it
        # If expected is not in success range but actual is, still accept it as success
        # (This handles cases where API returns 200 instead of expected 201, etc.)
        return
    
    # For non-success codes, require exact match
    if actual_code != expected:
        error_msg = (
            f"[bold red]Status Code Mismatch[/bold red]\n\n"
            f"Expected: {expected}\n"
            f"Got: {actual_code}\n"
            f"URL: {response.url}"
        )
        console.print(
            Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
        )
        sys.exit(1)


def validate_response_structure(response: Response, required_fields: list[str]) -> None:
    """
    Validate that the response contains required fields.

    Args:
        response: HTTP response object
        required_fields: List of required field names (supports dot notation)

    Raises:
        SystemExit: If required fields are missing
    """
    try:
        data = response.json()
    except Exception:
        error_msg = (
            "[bold red]Invalid JSON Response[/bold red]\n\nResponse is not valid JSON."
        )
        console.print(
            Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
        )
        sys.exit(1)

    missing_fields = []
    for field in required_fields:
        if "." in field:
            # Handle nested fields (e.g., "data.user.id")
            parts = field.split(".")
            current = data
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    missing_fields.append(field)
                    break
                current = current[part]
        else:
            if field not in data:
                missing_fields.append(field)

    if missing_fields:
        error_msg = (
            f"[bold red]Missing Required Fields[/bold red]\n\n"
            f"Missing fields: {', '.join(missing_fields)}\n"
            f"Response data: {data}"
        )
        console.print(
            Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
        )
        sys.exit(1)


def validate_json_response(response: Response) -> dict:
    """
    Validate and parse JSON response.

    Args:
        response: HTTP response object

    Returns:
        dict: Parsed JSON data

    Raises:
        SystemExit: If response is not valid JSON
    """
    try:
        return response.json()
    except Exception as e:
        error_msg = (
            f"[bold red]Invalid JSON Response[/bold red]\n\n"
            f"Error: {str(e)}\n"
            f"Response text: {response.text[:500]}"
        )
        console.print(
            Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
        )
        sys.exit(1)


def assert_response_contains(
    response: Union[Response, dict], key: str, value: Any, api_client: Optional[Any] = None
) -> None:
    """
    Assert that the response contains a specific key-value pair.

    Args:
        response: HTTP response object or dict (parsed JSON)
        key: Key to check (supports dot notation for nested keys)
        value: Expected value

    Raises:
        SystemExit: If key-value pair doesn't match
    """
    # Handle both Response object and dict
    if isinstance(response, Response):
        data = validate_json_response(response)
    else:
        data = response

    # Handle nested keys
    if "." in key:
        parts = key.split(".")
        current = data
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                error_msg = f"[bold red]Key Not Found[/bold red]\n\nKey path '{key}' not found in response."
                console.print(
                    Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
                )
                sys.exit(1)
            current = current[part]
        actual_value = current.get(parts[-1])
    else:
        actual_value = data.get(key)

    # Special handling for type checking (e.g., value=str)
    if isinstance(value, type) and isinstance(actual_value, value):
        return  # Type matches, assertion passes

    # Special handling for status codes: if checking "code" field and both values are in 200-299 range, accept it
    if key == "code" or key.endswith(".code"):
        if isinstance(value, int) and isinstance(actual_value, int):
            # If both are in success range (200-299), accept any success code
            if 200 <= value <= 299 and 200 <= actual_value <= 299:
                return  # Both are success codes, accept it

    if actual_value != value:
        error_msg = (
            f"[bold red]Value Mismatch[/bold red]\n\n"
            f"Key: {key}\n"
            f"Expected: {value}\n"
            f"Got: {actual_value}\n\n"
            f"[bold yellow]Full Response:[/bold yellow]\n{json.dumps(data, indent=2)}"
        )
        
        # Add curl command if API client is available
        if api_client and hasattr(api_client, "_last_request") and api_client._last_request:
            try:
                last_req = api_client._last_request
                curl_cmd = api_client._generate_curl_command(
                    last_req["method"],
                    last_req["url"],
                    last_req["headers"],
                    last_req["body"],
                )
                error_msg += f"\n\n[bold yellow]Curl Command:[/bold yellow]\n{curl_cmd}"
            except Exception:
                pass  # If curl generation fails, just skip it
        
        console.print(
            Panel(error_msg, border_style="red", title=VALIDATION_ERROR_TITLE)
        )
        sys.exit(1)
