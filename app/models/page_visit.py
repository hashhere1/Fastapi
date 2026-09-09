from sqlalchemy import Integer, Column, String, Float, DateTime
from app.database import Base
from sqlalchemy.sql import func

class PageVisit(Base):
    __tablename__ = "page_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    client_ip = Column(String, nullable=True)
    visited_at = Column(DateTime(timezone=True), server_default=func.now())
