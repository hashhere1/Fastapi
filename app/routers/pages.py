from fastapi import Request, APIRouter, Form, Depends
from fastapi.templating import Jinja2Templates
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi.templating import Jinja2Templates
from app.schemas.user import UserCreate
from pydantic import ValidationError


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {})

@router.get("/user-profile")
def get_user_profile(request: Request, user_id: int = None, db: Session = Depends(get_db)):
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse(request, "user_profile.html", {"user": user})

@router.post("/user-profile")
def save_user_profile(
    request: Request, user_id : str = Form(""), name : str = Form(...), email : str = Form(...), bio : str = Form(""), db : Session = Depends(get_db)
):
    try:
        validated_data = UserCreate(name=name, email=email, bio=bio)
    except ValidationError as e:
        return templates.TemplateResponse(request, "user_profile.html", {
            "user": None,
            "errors": e.errors()
        })
    if user_id:
        user = db.query(User).filter(User.id == int(user_id)).first()
        user.name = validated_data.name
        user.email = validated_data.email
        user.bio = validated_data.bio
    else:
        user = User(name=validated_data.name, email=validated_data.email, bio= validated_data.bio)
        db.add(user)

    db.commit()
    db.refresh(user)
    return templates.TemplateResponse(request, "user_profile.html", {"user": user})


