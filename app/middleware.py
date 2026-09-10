import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
from app.models.page_visit import PageVisit
from app.utils.security import decode_access_token
from app.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        token = request.cookies.get("access_token")
        request.state.user = None

        if token:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            payload = decode_access_token(token)
            if payload and "sub" in payload:
                user_id = payload["sub"]
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        request.state.user = user
                finally:
                    db.close()

        response = await call_next(request)
        return response


class TimeTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        client_ip = request.client.host

        db = SessionLocal()
        try:
            visit = PageVisit(path=request.url.path, duration=duration, client_ip=client_ip)
            db.add(visit)
            db.commit()
        finally:
            db.close()
            
        return response