from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.models.habit import Habit
from app.models.entry import HabitEntry
from app.models.streak import Streak
from app.routers.auth import get_current_user_from_cookie
from app.core.predictor import predict_habit_risk

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/predict", response_class=HTMLResponse)
def predict_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()

    predictions = []
    for habit in habits:
        entries = db.query(HabitEntry).filter_by(habit_id=habit.id).all()
        streak = db.query(Streak).filter_by(habit_id=habit.id).first()
        last_30 = today - timedelta(days=30)
        completed = [e for e in entries if e.entry_date >= last_30]
        completion_rate = (len(completed) / 30) * 100 if completed else 0

        prob, msg = predict_habit_risk(habit.name, streak, completion_rate, habit.difficulty)
        risk = 100 - prob  # risk percentage

        predictions.append({
            "habit": habit.name,
            "prob": prob,
            "risk": risk,
            "message": msg,
        })

    return templates.TemplateResponse("predict.html", {
        "request": request,
        "user": user,
        "predictions": predictions
    })
