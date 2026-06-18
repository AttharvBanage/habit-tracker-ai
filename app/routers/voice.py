from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user_from_cookie
from app.models.habit import Habit
from app.models.entry import HabitEntry
from datetime import date

router = APIRouter()

@router.post("/voice/log")
def voice_log_command(request: Request, command: str = Form(...), db: Session = Depends(get_db)):
    """Handles spoken commands and logs the habit if matched."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    command_lower = command.lower()

    # Try to find a matching habit name in user's list
    habit = (
        db.query(Habit)
        .filter(Habit.user_id == user.id)
        .filter(Habit.name.ilike(f"%{command_lower.split()[0]}%"))
        .first()
    )

    if not habit:
        return JSONResponse({"status": "fail", "message": "No matching habit found."})

    # Log today's completion
    exists = (
        db.query(HabitEntry)
        .filter(HabitEntry.user_id == user.id)
        .filter(HabitEntry.habit_id == habit.id)
        .filter(HabitEntry.entry_date == date.today())
        .first()
    )
    if not exists:
        entry = HabitEntry(user_id=user.id, habit_id=habit.id, entry_date=date.today())
        db.add(entry)
        db.commit()
        return JSONResponse({"status": "success", "message": f"Marked '{habit.name}' as done!"})
    else:
        return JSONResponse({"status": "exists", "message": f"'{habit.name}' is already marked complete today."})
