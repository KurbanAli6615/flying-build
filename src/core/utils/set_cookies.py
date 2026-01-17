from fastapi.responses import JSONResponse

from apps.user.schemas import TokensResponse
from config import settings
from core.types import RoleType


def set_auth_cookies(
    response: JSONResponse, tokens: TokensResponse, role: RoleType
) -> JSONResponse:
    """
    Attach authentication cookies to the given HTTP response according to the user's role.
    
    For RoleType.USER sets `accessToken` and `refreshToken`; for RoleType.ADMIN sets `adminAccessToken` and `adminRefreshToken`. Cookie attributes (domain, secure, samesite, httponly, expires) are chosen based on environment settings.
    
    Parameters:
        response (JSONResponse): The HTTP response to modify.
        tokens (TokensResponse): Object containing `access_token` and `refresh_token` used as cookie values.
        role (RoleType): Role that determines which cookie names are set (user or admin).
    
    Returns:
        JSONResponse: The same response object with the authentication cookies attached.
    """

    production_cookies_params = {
        "domain": settings.COOKIES_DOMAIN,
        "secure": True,
        "samesite": "lax" if settings.is_production else "none",
        "httponly": True,
    }

    development_cookies_params = {
        "domain": settings.COOKIES_DOMAIN,
        "secure": False,
        "samesite": "lax",
        "httponly": True,
    }

    cookies_params = (
        production_cookies_params
        if settings.is_production
        else development_cookies_params
    )

    if role == RoleType.USER:
        response.set_cookie(
            "accessToken",
            tokens.access_token,
            expires=int(settings.ACCESS_TOKEN_EXP),
            **cookies_params,
        )
        response.set_cookie(
            "refreshToken",
            tokens.refresh_token,
            expires=int(settings.REFRESH_TOKEN_EXP),
            **cookies_params,
        )
    if role == RoleType.ADMIN:
        response.set_cookie(
            "adminAccessToken",
            tokens.access_token,
            expires=int(settings.ACCESS_TOKEN_EXP),
            **cookies_params,
        )
        response.set_cookie(
            "adminRefreshToken",
            tokens.refresh_token,
            expires=int(settings.REFRESH_TOKEN_EXP),
            **cookies_params,
        )
    return response


def delete_cookies(response: JSONResponse, role: RoleType) -> JSONResponse:
    """
    Delete authentication cookies from an HTTP response.
    This function takes an HTTP response object and removes the "accessToken" and "refreshToken" cookies
    from the response, making them invalid for subsequent requests.
    Args:
        response (Response): The HTTP response object to remove cookies from.
        role(Role type): The role type of user.
    Returns:
        Response: The updated HTTP response with the cookies removed.
    """
    cookie_params = {
        "domain": settings.COOKIES_DOMAIN,
        "secure": True,
        "samesite": "lax" if settings.is_production else "none",
        "httponly": False,
    }

    if role == RoleType.USER:
        response.delete_cookie("accessToken", **cookie_params)
        response.delete_cookie("refreshToken", **cookie_params)
    elif role == RoleType.ADMIN:
        response.delete_cookie("adminAccessToken", **cookie_params)
        response.delete_cookie("adminRefreshToken", **cookie_params)

    return response