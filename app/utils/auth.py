from fastapi.responses import RedirectResponse
from .security import create_access_token

def create_auth_redirect_response(user_id: int, redirect_url: str = "/users") -> RedirectResponse:
    token = create_access_token(data={"sub": str(user_id)})
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite= "lax",
        secure=False
    )
    return response