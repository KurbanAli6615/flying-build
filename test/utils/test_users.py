from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test.utils.api_client import APIClient


class TestUserManager:
    """
    Manages test users for API testing.

    Provides predefined test users and methods to create them via API.
    """

    @staticmethod
    def get_test_user_1(config) -> dict:
        """
        Get predefined test user 1 data.

        Args:
            config: Test configuration instance

        Returns:
            dict: Test user 1 data
        """
        user_1, _ = config.get_test_users()
        return user_1

    @staticmethod
    def get_test_user_2(config) -> dict:
        """
        Get predefined test user 2 data.

        Args:
            config: Test configuration instance

        Returns:
            dict: Test user 2 data
        """
        _, user_2 = config.get_test_users()
        return user_2

    @staticmethod
    async def create_test_user(
        api_client: "APIClient", user_data: dict, encryption_helper
    ) -> dict:
        """
        Create a test user via API.

        Args:
            api_client: The API client instance
            user_data: User data dictionary with fields:
                - name
                - username
                - email
                - country_code
                - phone
                - password
            encryption_helper: EncryptionHelper instance

        Returns:
            dict: Response data from user creation
        """
        # Encrypt user data
        encrypted_payload = await encryption_helper.prepare_encrypted_request(
            user_data, api_client
        )

        # Create user via API
        response = await api_client.post("/user", json=encrypted_payload)
        response_data = response.json()

        if response_data.get("status") == "success":
            return response_data.get("data", {})

        raise ValueError(f"Failed to create test user: {response_data}")

    @staticmethod
    async def ensure_test_users_exist(
        api_client: "APIClient", config, encryption_helper
    ) -> tuple[dict, dict]:
        """
        Ensure test users exist, creating them if necessary.

        Args:
            api_client: The API client instance
            config: Test configuration instance
            encryption_helper: EncryptionHelper instance

        Returns:
            tuple[dict, dict]: Response data for user 1 and user 2
        """
        user_1_data = TestUserManager.get_test_user_1(config)
        user_2_data = TestUserManager.get_test_user_2(config)

        # Create both users
        user_1_response = await TestUserManager.create_test_user(
            api_client, user_1_data, encryption_helper
        )
        user_2_response = await TestUserManager.create_test_user(
            api_client, user_2_data, encryption_helper
        )

        return user_1_response, user_2_response
