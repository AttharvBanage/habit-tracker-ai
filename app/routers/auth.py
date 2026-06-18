from fastapi import APIRouter, Depends, Request, Form, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()
    except JWTError:
        return None


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mode": "register"})


@router.post("/register")
def register_user(request: Request, email: str = Form(...), password: str = Form(...),
                  name: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("login.html", {"request": request, "error": "Email already registered."})
    user = User(email=email, password_hash=hash_password(password), name=name)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mode": "login"})


@router.post("/login")
def login_user(request: Request, email: str = Form(...), password: str = Form(...),
               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})
    token = create_access_token({"sub": email})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie("access_token", token, httponly=True)
    return response


# ✅ NEW: Logout route
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
