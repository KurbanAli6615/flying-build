from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test.utils.api_client import APIClient


class EncryptionHelper:
    """
    Helper for RSA/AES encryption used in API requests.

    Provides methods to get public key and encrypt payloads
    for API requests that require encryption.
    """

    _public_key_cache: str | None = None

    @staticmethod
    async def get_public_key(api_client: "APIClient") -> str:
        """
        Get the RSA public key from the API.

        Caches the public key to avoid repeated API calls.

        Args:
            api_client: The API client instance

        Returns:
            str: Public key in PEM format

        Raises:
            ValueError: If public key retrieval fails, includes curl command in error message
        """
        # Return cached key if available
        if EncryptionHelper._public_key_cache:
            return EncryptionHelper._public_key_cache

        try:
            # Fetch public key from API
            response = await api_client.get("/user/public-key")
            response_data = response.json()

            # Extract public key from response - note: constants.SUCCESS = "SUCCESS" (uppercase)
            if response_data.get("status") == "SUCCESS" and response_data.get("data"):
                public_key = response_data["data"].get("publicKey")
                if public_key:
                    EncryptionHelper._public_key_cache = public_key
                    return public_key

            # If we get here, the response structure is wrong
            # Generate curl command for debugging
            import json

            # Get headers that would be used in the request
            headers = dict(api_client.client.headers)
            if api_client._cookies:
                # Add cookies to headers for curl command
                cookie_str = "; ".join(
                    [f"{k}={v}" for k, v in api_client._cookies.items()]
                )
                headers["Cookie"] = cookie_str
            curl_cmd = api_client._generate_curl_command(
                "GET", f"{api_client.base_url}/user/public-key", headers, None
            )
            error_msg = (
                f"Failed to retrieve public key from API\n\n"
                f"Response: {json.dumps(response_data, indent=2)}\n\n"
                f"Curl Command:\n{curl_cmd}"
            )
            raise ValueError(error_msg)
        except ValueError:
            # Re-raise ValueError with curl command if not already included
            raise
        except Exception as e:
            # For any other exception, include curl command
            import json

            # Get headers that would be used in the request
            headers = dict(api_client.client.headers)
            if api_client._cookies:
                # Add cookies to headers for curl command
                cookie_str = "; ".join(
                    [f"{k}={v}" for k, v in api_client._cookies.items()]
                )
                headers["Cookie"] = cookie_str
            curl_cmd = api_client._generate_curl_command(
                "GET", f"{api_client.base_url}/user/public-key", headers, None
            )
            error_msg = f"{str(e)}\n\nCurl Command:\n{curl_cmd}"
            raise ValueError(error_msg) from e

    @staticmethod
    async def encrypt_payload(data: dict, api_client: "APIClient") -> dict[str, str]:
        """
        Encrypt a payload using the API's encryption endpoint.

        Args:
            data: Dictionary data to encrypt
            api_client: The API client instance

        Returns:
            dict: Encrypted request with keys: encrypted_data, encrypted_key, iv

        Raises:
            ValueError: If encryption fails, includes curl command in error message
        """
        # Use the API's encrypt-data endpoint
        try:
            response = await api_client.post("/encrypt-data", json=data)
            response_data = response.json()

            # Check response structure - note: constants.SUCCESS = "SUCCESS" (uppercase)
            # Response from /encrypt-data endpoint (src/core/data_encrypt/controller/encrypt_decrypt.py):
            # { status: "SUCCESS", code: 200, data: { encrypted_data, encrypted_key, iv } }
            # Note: The data keys are in snake_case, not camelCase
            if response_data.get("status") == "SUCCESS" and response_data.get("data"):
                encrypted_data = response_data["data"]
                return {
                    "encrypted_data": encrypted_data.get("encrypted_data"),
                    "encrypted_key": encrypted_data.get("encrypted_key"),
                    "iv": encrypted_data.get("iv"),
                }

            # If we get here, the response structure is wrong
            # Generate curl command for debugging
            import json

            # Get headers that would be used in the request
            headers = dict(api_client.client.headers)
            if api_client._cookies:
                # Add cookies to headers for curl command
                cookie_str = "; ".join(
                    [f"{k}={v}" for k, v in api_client._cookies.items()]
                )
                headers["Cookie"] = cookie_str
            curl_cmd = api_client._generate_curl_command(
                "POST", f"{api_client.base_url}/encrypt-data", headers, data
            )
            error_msg = (
                f"Failed to encrypt payload via API\n\n"
                f"Response: {json.dumps(response_data, indent=2)}\n\n"
                f"Curl Command:\n{curl_cmd}"
            )
            raise ValueError(error_msg)
        except ValueError:
            # Re-raise ValueError with curl command if not already included
            raise
        except Exception as e:
            # For any other exception, include curl command
            import json

            # Get headers that would be used in the request
            headers = dict(api_client.client.headers)
            if api_client._cookies:
                # Add cookies to headers for curl command
                cookie_str = "; ".join(
                    [f"{k}={v}" for k, v in api_client._cookies.items()]
                )
                headers["Cookie"] = cookie_str
            curl_cmd = api_client._generate_curl_command(
                "POST", f"{api_client.base_url}/encrypt-data", headers, data
            )
            error_msg = f"{str(e)}\n\nCurl Command:\n{curl_cmd}"
            raise ValueError(error_msg) from e

    @staticmethod
    async def prepare_encrypted_request(
        data: dict, api_client: "APIClient"
    ) -> dict[str, str]:
        """
        Prepare an encrypted request payload.

        This is a convenience method that encrypts data using the API's
        encryption endpoint.

        Args:
            data: Dictionary data to encrypt
            api_client: The API client instance

        Returns:
            dict: Encrypted request payload ready for API calls
        """
        return await EncryptionHelper.encrypt_payload(data, api_client)

    @staticmethod
    def clear_cache() -> None:
        """Clear the cached public key."""
        EncryptionHelper._public_key_cache = None
