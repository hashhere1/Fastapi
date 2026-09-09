import os
import uuid
import shutil
from fastapi import Request, APIRouter, Form, Depends, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi.templating import Jinja2Templates
from app.schemas.user import UserCreate, UserUpdate
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.file_upload import upload_image

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {})

@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse(request, "users.html", {"users": users})

@router.get("/users/new")            
def new_user_form(request: Request):
    return templates.TemplateResponse(request, "user_profile.html", {"user": None})

@router.get("/users/{user_id}")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return templates.TemplateResponse(request, "user_profile.html", {"user": user})

@router.post("/users")
def save_user_profile(
    request: Request,
    user_data: Annotated[UserCreate, Depends(UserCreate.as_form)],
    profile_pic: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_path = upload_image(profile_pic)
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "user_profile.html",
            {
                "user": None,
                "errors": [e.detail]
            }
        )

    user = User(name = user_data.name, email = user_data.email, bio = user_data.bio, profile_pic = file_path)

    db.add(user)
    db.commit()
    db.refresh(user)
    return RedirectResponse(
        url="/users",
        status_code=303
    )

@router.patch("/users/{user_id}")
def update_user(
    request: Request,
    user_id: int,
    user_data: Annotated[UserUpdate, Depends(UserUpdate.as_form)],
    profile_pic: UploadFile | None = File(None),
    db: Session = Depends(get_db)
                ):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.bio is not None:
        user.bio = user_data.bio

    
    try:
        if profile_pic:
            file_path = upload_image(profile_pic)

            user.profile_pic = file_path
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "user_profile.html",
            {
                "user": user,
                "errors": [e.detail],
            }
        )

    db.commit()
    db.refresh(user)

    return RedirectResponse(
        url="/users",
        status_code=303
    )

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user)
    db.commit()

    return RedirectResponse(url="/users", status_code=303)    


