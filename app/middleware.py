import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
from app.models.page_visit import PageVisit

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