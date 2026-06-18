from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routers.auth import get_current_user_from_cookie
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
