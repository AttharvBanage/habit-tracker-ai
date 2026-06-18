from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user_from_cookie
from app.core.ai_coach_engine import generate_ai_insight

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/coach", response_class=HTMLResponse)
def ai_coach_dashboard(request: Request, db: Session = Depends(get_db)):
    """AI Coach Dashboard — personalized insights & motivation."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    ai_data = generate_ai_insight(db, user)

    return templates.TemplateResponse("coach.html", {
        "request": request,
        "user": user,
        "ai_data": ai_data
    })
