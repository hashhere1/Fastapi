import os
from fastapi import Request, APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.templating import Jinja2Templates
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserLogin
from fastapi.responses import RedirectResponse
from typing import Annotated
from app.utils.file_upload import upload_image
from app.utils.security import hash_password, verify_password
from app.utils.auth import create_auth_redirect_response
from app.utils.dependencies import get_current_user, require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {})

@router.get("/users")
def list_users(request: Request,
               _: User = Depends(require_login), 
               db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse(request, "users.html", {"users": users})

@router.get("/users/new")            
def new_user_form(
    request: Request,
    _: User = Depends(require_login),
    ):
    return templates.TemplateResponse(request, "user_profile.html", {"user": None})

@router.get("/users/{user_id}")
def get_user(request: Request, 
             user_id: int,
             _: User = Depends(require_login), 
             db: Session = Depends(get_db)
             ):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return templates.TemplateResponse(request, "user_profile.html", {"user": user})

@router.post("/users")
def save_user_profile(
    request: Request,
    user_data: Annotated[UserCreate, Depends(UserCreate.as_form)],
    profile_pic: UploadFile = File(...),
    _: User = Depends(require_login),
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
    current_user: User = Depends(get_current_user),
    profile_pic: UploadFile | None = File(None),
    db: Session = Depends(get_db)
                ):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this profile"
        )
    
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
            },
            status_code=400
        )

    db.commit()
    db.refresh(user)

    return RedirectResponse(
        url="/users",
        status_code=303
    )

@router.delete("/users/{user_id}")
def delete_user(user_id: int, 
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()


    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authenticated to delete this account"
        )

    if user.profile_pic:
        full_path = os.path.join("app/uploads", user.profile_pic)
        if os.path.exists(full_path):
            os.remove(full_path)

    db.delete(user)
    db.commit()

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response



@router.get("/register")
def register_page(request: Request):
    if request.state.user:
        return RedirectResponse(url="/users", status_code=303)
    return templates.TemplateResponse(request, "register.html", {})


@router.post("/register")
def register_user(
    request: Request,
    user_data: Annotated[UserCreate, Depends(UserCreate.as_form)],
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": ["Email is already registered"]},
            status_code=400
        )
    hashed_pwd = hash_password(user_data.password)

    new_user = User(
        name = user_data.name,
        email = user_data.email,
        hashed_password = hashed_pwd,
        bio = user_data.bio
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return create_auth_redirect_response(user_id=new_user.id, redirect_url="/users")

@router.get("/login")
def login_page(request: Request):
    if request.state.user:
        return RedirectResponse(url="/users", status_code=303)
    return templates.TemplateResponse(request, "login.html", {})

@router.post("/login")
def login_user(
    request: Request,
    credentials: Annotated[UserLogin, Depends(UserLogin.as_form)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid email or password"},
            status_code=401
        )
    return create_auth_redirect_response(user_id=user.id, redirect_url="/users")


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response