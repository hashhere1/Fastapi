from fastapi import FastAPI
from app.routers import pages
from app.database import Base, engine
from app.middleware import TimeTrackingMiddleware
from app.models.page_visit import PageVisit
from app.models.user import User
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")
app.add_middleware(TimeTrackingMiddleware)
app.include_router(pages.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)