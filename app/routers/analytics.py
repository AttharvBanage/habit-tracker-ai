from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.models.habit import Habit
from app.models.entry import HabitEntry
from app.models.streak import Streak
from app.routers.auth import get_current_user_from_cookie
from app.core.utils import compute_consistency_score

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/analytics", response_class=HTMLResponse)
def analytics_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")

    today = date.today()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    analytics = []

    for habit in habits:
        entries = db.query(HabitEntry).filter_by(habit_id=habit.id).all()
        streak = db.query(Streak).filter_by(habit_id=habit.id).first()
        last_60 = today - timedelta(days=60)
        completed = [e for e in entries if e.entry_date >= last_60]
        completion_rate = (len(completed) / 60) * 100 if completed else 0

        score = compute_consistency_score(streak, habit.difficulty, completion_rate)

        if score > 80:
            insight = "🔥 Excellent consistency — you’re unstoppable!"
        elif score > 60:
            insight = "⚡ Solid progress! Stay focused to push further."
        elif score > 40:
            insight = "💡 You're doing okay — a bit more regularity can boost this."
        else:
            insight = "🚀 Let's restart momentum — small steps daily."

        analytics.append({
            "habit": habit.name,
            "score": score,
            "streak": streak.current_streak if streak else 0,
            "best_streak": streak.best_streak if streak else 0,
            "completion": round(completion_rate, 1),
            "insight": insight
        })

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "user": user,
        "analytics": analytics
    })
