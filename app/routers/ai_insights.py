from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Habit, HabitEntry, User
from app.core.database import get_db
from app.routers.auth import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/predict", response_class=HTMLResponse)
def ai_insights(request: Request, db: Session = Depends(get_db)):
    """Show AI-driven habit recommendations and trend predictions."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()
    last_14_days = today - timedelta(days=14)

    # Fetch habits and completion logs
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    entries = db.query(HabitEntry).filter(
        HabitEntry.user_id == user.id, HabitEntry.entry_date >= last_14_days
    ).all()

    # Compute consistency
    habit_logs = {habit.id: 0 for habit in habits}
    for entry in entries:
        if entry.habit_id in habit_logs:
            habit_logs[entry.habit_id] += 1

    insights = []
    for habit in habits:
        total_days = (today - habit.start_date).days + 1
        completions = habit_logs.get(habit.id, 0)
        consistency = round((completions / total_days) * 100, 1) if total_days > 0 else 0

        prediction = "🔥 Excellent! Keep it up!" if consistency >= 80 else (
            "⚡ Doing well, aim for higher streaks!" if consistency >= 50 else
            "🚀 Try setting smaller, consistent goals."
        )

        insights.append({
            "name": habit.name,
            "category": habit.category.name if habit.category else "General",
            "consistency": consistency,
            "prediction": prediction
        })

    return templates.TemplateResponse("predict.html", {
        "request": request,
        "user": user,
        "insights": insights,
    })
