from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.models.habit import Habit
from app.models.entry import HabitEntry
from app.models.streak import Streak
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_current_user(db: Session):
    return db.query(User).first()  # demo only

@router.post("/habits/{habit_id}/complete")
def mark_complete(habit_id: int, db: Session = Depends(get_db)):
    user = get_current_user(db)
    today = date.today()

    # check if already logged
    existing = db.query(HabitEntry).filter_by(habit_id=habit_id, entry_date=today).first()
    if existing:
        return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)

    # log entry
    entry = HabitEntry(habit_id=habit_id, user_id=user.id, entry_date=today)
    db.add(entry)

    # update streak
    streak = db.query(Streak).filter_by(habit_id=habit_id).first()
    if not streak:
        streak = Streak(habit_id=habit_id, current_streak=1, best_streak=1, last_date=today)
        db.add(streak)
    else:
        if streak.last_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.last_date = today
        if streak.current_streak > streak.best_streak:
            streak.best_streak = streak.current_streak
    db.commit()

    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)
from datetime import date, timedelta
import random

@router.get("/habits/{habit_id}/progress", response_class=HTMLResponse)
def view_progress(request: Request, habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).get(habit_id)
    entries = db.query(HabitEntry).filter_by(habit_id=habit_id).order_by(HabitEntry.entry_date).all()
    streak = db.query(Streak).filter_by(habit_id=habit_id).first()

    # Create 60-day window
    today = date.today()
    start_date = today - timedelta(days=59)
    heatmap_data = []

    # Map entries by date
    entry_dates = {e.entry_date for e in entries}

    for i in range(60):
        day = start_date + timedelta(days=i)
        completed = 1 if day in entry_dates else 0
        heatmap_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "value": completed
        })

    # AI-style insight (placeholder)
    completion_rate = round((len(entry_dates)/60)*100, 1)
    insight = (
        "🔥 You're building solid momentum!" if completion_rate > 70 else
        "💡 Try to log more consistently this week!"
    )

    return templates.TemplateResponse("habit_progress_heatmap.html", {
        "request": request,
        "habit": habit,
        "streak": streak,
        "heatmap_data": heatmap_data,
        "completion_rate": completion_rate,
        "insight": insight
    })
