from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse

import constants
from core.data_encrypt.schemas import EncryptedRequest
from core.data_encrypt.services.data_decrypt_service import DataEncryptService

router = APIRouter(tags=["Data Encryption Decryption"])


@router.post(
    "/decrypt-data",
    status_code=status.HTTP_200_OK,
    name="decrypt-data",
    description="Decrypt Data",
    operation_id="decrypt_data_admin",
)
async def decrypt_data_handler(
    request: Request,
    body: EncryptedRequest,
    service: Annotated[DataEncryptService, Depends()],
) -> JSONResponse:
    """
    Decrypt data using RSA and AES.
    """
    res = await service.decrypt_data_admin(request=request, encrypted_request=body)
    data = {"status": constants.SUCCESS,
            "code": status.HTTP_200_OK, "data": res}
    response = JSONResponse(content=data)
    return response


@router.post(
    "/encrypt-data",
    status_code=status.HTTP_200_OK,
    name="encrypt-data",
    description="Encrypt Data",
    operation_id="encrypt_data",
)
async def encrypt_data(
    service: Annotated[DataEncryptService, Depends()], body: Annotated[Any, Body()]
) -> JSONResponse:
    """
    to get encrypted data for user
    """

    encrypted_data, encrypted_key, iv = service.encrypt_data(data=body)

    result = {
        "encrypted_data": encrypted_data,
        "encrypted_key": encrypted_key,
        "iv": iv,
    }

    response_data = {
        "status": constants.SUCCESS,
        "code": status.HTTP_200_OK,
        "data": result,
    }
    return JSONResponse(content=response_data)
