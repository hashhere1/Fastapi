from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.models.user import User


class LoginRequired(Exception):
    pass


def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Required"
        )
    return user

def require_login(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise LoginRequired()
    return user