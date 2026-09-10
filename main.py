from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from app.routers import pages
from app.middleware import TimeTrackingMiddleware, AuthMiddleware
from app.models.page_visit import PageVisit
from app.models.user import User
from fastapi.staticfiles import StaticFiles
from app.utils.dependencies import LoginRequired
import uvicorn

app = FastAPI()

@app.exception_handler(LoginRequired)
async def login_required_handler(request: Request, exc: LoginRequired):
    return RedirectResponse(
        url="/login",
        status_code=303
    )

app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")
app.add_middleware(AuthMiddleware)
app.add_middleware(TimeTrackingMiddleware)
app.include_router(pages.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)