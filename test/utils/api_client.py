import json
import sys
from typing import Any, Optional

import httpx
from httpx import Response
from rich.console import Console
from rich.panel import Panel

console = Console()


class APIClient:
    """
    Async HTTP client with error handling and request/response logging.

    Provides methods for making HTTP requests with automatic error handling.
    On failure, prints detailed request/response information and exits.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialize the API client.

        Args:
            base_url: Base URL for API requests (e.g., "http://localhost:8000")
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self._cookies: dict[str, str] = {}
        # Store last request details for validators to generate curl commands
        self._last_request: dict[str, Any] = {}

    async def __aenter__(self) -> "APIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.client.aclose()

    def _format_request_details(
        self, method: str, url: str, headers: dict, body: Any
    ) -> str:
        """
        Format request details for error display.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body

        Returns:
            str: Formatted request details
        """
        details = f"[bold]Method:[/bold] {method}\n"
        details += f"[bold]URL:[/bold] {url}\n"
        details += "[bold]Headers:[/bold]\n"
        for key, value in headers.items():
            details += f"  {key}: {value}\n"

        if body:
            if isinstance(body, dict):
                body_str = json.dumps(body, indent=2)
            else:
                body_str = str(body)
            details += f"[bold]Body:[/bold]\n{body_str}"

        # Generate curl command
        details += "\n[bold]Curl Command:[/bold]\n"
        curl_cmd = self._generate_curl_command(method, url, headers, body)
        details += f"  {curl_cmd}"

        return details

    def _generate_curl_command(
        self, method: str, url: str, headers: dict, body: Any
    ) -> str:
        """
        Generate a curl command equivalent to the request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body

        Returns:
            str: Curl command string
        """
        # Build curl command
        curl_parts = [f"curl -X '{method.upper()}'"]
        curl_parts.append(f"  '{url}'")

        # Track if Content-Type is already added
        content_type_added = False

        # Add headers
        for key, value in headers.items():
            # Skip cookie header - we'll add it separately if needed
            if key.lower() == "cookie":
                continue
            # Escape single quotes in header values
            escaped_value = str(value).replace("'", "'\"'\"'")
            curl_parts.append(f"  -H '{key}: {escaped_value}'")
            if key.lower() == "content-type":
                content_type_added = True

        # Add cookies if present
        cookie_value = headers.get("Cookie") or headers.get("cookie")
        if cookie_value:
            escaped_cookie = str(cookie_value).replace("'", "'\"'\"'")
            curl_parts.append(f"  -H 'Cookie: {escaped_cookie}'")

        # Add body for POST/PUT/PATCH
        if body and method.upper() in ["POST", "PUT", "PATCH"]:
            if isinstance(body, dict):
                body_json = json.dumps(body)
                # Escape for shell - handle both single and double quotes
                body_json = body_json.replace("'", "'\"'\"'").replace('"', '\\"')
                curl_parts.append(f"  -d '{body_json}'")
                if not content_type_added:
                    curl_parts.append("  -H 'Content-Type: application/json'")
            else:
                body_str = str(body).replace("'", "'\"'\"'")
                curl_parts.append(f"  -d '{body_str}'")

        return " \\\n".join(curl_parts)

    def _format_response_details(self, response: Response) -> str:
        """
        Format response details for error display.

        Args:
            response: HTTP response object

        Returns:
            str: Formatted response details
        """
        details = f"[bold]Status Code:[/bold] {response.status_code}\n"
        details += "[bold]Headers:[/bold]\n"
        for key, value in response.headers.items():
            details += f"  {key}: {value}\n"

        # Try to get response body and extract error message
        error_message = None
        try:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = response.json()
                    if isinstance(body, dict):
                        # Extract error message from common fields
                        error_message = (
                            body.get("message") 
                            or body.get("error") 
                            or body.get("detail")
                            or (body.get("data", {}).get("message") if isinstance(body.get("data"), dict) else None)
                        )
                        body_str = json.dumps(body, indent=2)
                    else:
                        body_str = str(body)
                    details += f"[bold]Body:[/bold]\n{body_str}"
                except Exception:
                    # If JSON parsing fails, try text
                    try:
                        details += f"[bold]Body:[/bold]\n{response.text}"
                    except Exception:
                        details += "[bold]Body:[/bold]\n[Unable to read response body]"
            else:
                try:
                    details += f"[bold]Body:[/bold]\n{response.text}"
                except Exception:
                    details += "[bold]Body:[/bold]\n[Unable to read response body]"
        except Exception as e:
            details += f"[bold]Body:[/bold]\n[Error reading response: {str(e)}]"
        
        # Add error message prominently if found
        if error_message:
            details += f"\n\n[bold red]Error Message:[/bold red] {error_message}"

        return details

    def _handle_error(
        self,
        method: str,
        url: str,
        response: Optional[Response] = None,
        error: Optional[Exception] = None,
        request_body: Any = None,
    ) -> None:
        """
        Handle API errors by printing details and exiting.

        Args:
            method: HTTP method
            url: Request URL
            response: Response object (if available)
            error: Exception object (if available)
            request_body: Request body that was sent (if available)
        """
        error_panel_content = "[bold red]API Request Failed[/bold red]\n\n"

        # Add request details
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        headers = dict(self.client.headers)
        if self._cookies:
            headers.update(self._cookies)

        error_panel_content += "[bold yellow]Request Details:[/bold yellow]\n"
        error_panel_content += self._format_request_details(
            method, full_url, headers, request_body
        )
        error_panel_content += "\n\n"

        # Add response details if available
        if response:
            error_panel_content += "[bold yellow]Response Details:[/bold yellow]\n"
            error_panel_content += self._format_response_details(response)
            error_panel_content += "\n\n"

        # Add error details if available
        if error:
            error_panel_content += f"[bold yellow]Error:[/bold yellow] {str(error)}\n"

        console.print(Panel(error_panel_content, border_style="red", title="Error"))
        sys.exit(1)

    async def _make_request(self, method: str, url: str, **kwargs) -> Response:
        """
        Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL (relative or absolute)
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object

        Raises:
            SystemExit: On request failure
        """
        # Extract request body for error reporting
        request_body = kwargs.get("json") or kwargs.get("data") or kwargs.get("content")

        # Update cookies in headers
        if self._cookies:
            if "cookies" not in kwargs:
                kwargs["cookies"] = {}
            kwargs["cookies"].update(self._cookies)

        try:
            response = await self.client.request(method, url, **kwargs)
            
            # Store last request details for validators to generate curl commands
            headers = dict(self.client.headers)
            if self._cookies:
                cookie_str = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                headers["Cookie"] = cookie_str
            
            self._last_request = {
                "method": method,
                "url": f"{self.base_url}{url}" if not url.startswith("http") else url,
                "headers": headers,
                "body": request_body,
            }

            # Update cookies from response
            if response.cookies:
                self._cookies.update(dict(response.cookies))

            # Check for error status codes (200-299 are success, 400+ are errors)
            if response.status_code < 200 or response.status_code >= 400:
                self._handle_error(
                    method, url, response=response, request_body=request_body
                )
                return response

            return response
        except httpx.HTTPError as e:
            self._handle_error(method, url, error=e, request_body=request_body)
            raise
        except Exception as e:
            self._handle_error(method, url, error=e, request_body=request_body)
            raise

    async def get(self, url: str, **kwargs) -> Response:
        """
        Make a GET request.

        Args:
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object
        """
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Response:
        """
        Make a POST request.

        Args:
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object
        """
        return await self._make_request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Response:
        """
        Make a PUT request.

        Args:
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object
        """
        return await self._make_request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Response:
        """
        Make a DELETE request.

        Args:
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object
        """
        return await self._make_request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Response:
        """
        Make a PATCH request.

        Args:
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response: HTTP response object
        """
        return await self._make_request("PATCH", url, **kwargs)

    def set_cookies(self, cookies: dict[str, str]) -> None:
        """
        Set cookies for subsequent requests.

        Args:
            cookies: Dictionary of cookie name-value pairs
        """
        self._cookies.update(cookies)

    def get_cookies(self) -> dict[str, str]:
        """
        Get current cookies.

        Returns:
            dict: Current cookies
        """
        return self._cookies.copy()

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self._cookies.clear()
