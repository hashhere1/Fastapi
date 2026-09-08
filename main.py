from fastapi import FastAPI
from app.routers import pages
from app.database import Base, engine
from app.middleware import TimeTrackingMiddleware
from app.models.page_visit import PageVisit
from app.models.user import User

app = FastAPI()

Base.metadata.create_all(bind= engine)
app.add_middleware(TimeTrackingMiddleware)
app.include_router(pages.router)