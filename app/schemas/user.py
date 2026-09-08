from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None