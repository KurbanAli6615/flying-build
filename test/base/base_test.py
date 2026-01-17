from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test.configuration.config import TestConfig
    from test.utils.api_client import APIClient


class BaseTestFeature(ABC):
    """
    Base class for all feature test suites.

    All feature tests should inherit from this class and implement
    the run_tests() method.
    """

    feature_name: str
    api_client: "APIClient"
    config: "TestConfig"

    def __init__(self, api_client: "APIClient", config: "TestConfig") -> None:
        """
        Initialize the test feature.

        Args:
            api_client: The API client instance for making HTTP requests
            config: The test configuration instance
        """
        self.api_client = api_client
        self.config = config

    async def setup(self) -> None:
        """
        Setup before running tests.

        Override this method in subclasses to perform any setup
        operations (e.g., creating test data, getting authentication tokens).
        """
        pass

    async def teardown(self) -> None:
        """
        Cleanup after tests.

        Override this method in subclasses to perform any cleanup
        operations (e.g., deleting test data, clearing cookies).
        """
        pass

    @abstractmethod
    async def run_tests(self) -> None:
        """
        Main test execution method.

        Must be implemented by each feature test class.
        This method should contain all the test steps for the feature.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run_tests() method"
        )

    def get_feature_name(self) -> str:
        """
        Return the feature name for CLI display.

        Returns:
            str: The feature name
        """
        return self.feature_name
