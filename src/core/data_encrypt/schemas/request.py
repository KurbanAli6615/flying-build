from pydantic import model_validator

from core.common_helpers import validate_string_fields
from core.utils import CamelCaseModel


class EncryptedRequest(CamelCaseModel):
    """
    request model for encrypted data
    """

    encrypted_data: str
    encrypted_key: str
    iv: str

    _validate_string_fields = model_validator(mode="before")(validate_string_fields)
