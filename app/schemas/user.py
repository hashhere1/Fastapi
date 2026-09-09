from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi import Form

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None

    @classmethod
    def as_form(
        cls, 
        name: str = Form(...),
        email: EmailStr = Form(...),
        bio: str | None = Form(None)  ):

        return cls(
            name = name,
            email = email,
            bio = bio
        )

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str | None = Form(None),
        email: EmailStr | None = Form(None),
        bio: str | None = Form(None)
    ):

        return cls(
            name = name,
            email = email,
            bio = bio
        )