from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.routers.auth import get_current_user_from_cookie
from app.core.ai_coach_engine import generate_ai_insight
from app.models.entry import HabitEntry

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/coach", response_class=HTMLResponse)
def ai_coach_page(request: Request, db: Session = Depends(get_db)):
    """Display the AI Coach insights page."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    ai_data = generate_ai_insight(db, user)

    # Build 7-day performance dataset
    today = date.today()
    labels, values = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = (
            db.query(HabitEntry)
            .filter(HabitEntry.user_id == user.id, HabitEntry.entry_date == d)
            .count()
        )
        labels.append(d.strftime("%a"))
        values.append(count)

    return templates.TemplateResponse(
        "coach.html",
        {
            "request": request,
            "user": user,
            "ai_data": ai_data,
            "chart_labels": labels,
            "chart_values": values,
        },
    )
