from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.models import Habit, Category, User, HabitEntry  # Safe unified import
from app.core.database import get_db
from app.core.xp_manager import add_xp
from app.routers.auth import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -----------------------------
# 📋 List Habits (Main Page)
# -----------------------------
@router.get("/habits", response_class=HTMLResponse)
def show_habits(request: Request, db: Session = Depends(get_db)):
    """Display all user habits + check which are done today."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()

    # Habits completed today
    completed_today = {
        e.habit_id for e in db.query(HabitEntry)
        .filter(HabitEntry.user_id == user.id, HabitEntry.entry_date == today)
        .all()
    }

    return templates.TemplateResponse("habits.html", {
        "request": request,
        "user": user,
        "habits": habits,
        "completed_today": completed_today
    })


# -----------------------------
# ➕ Add Habit
# -----------------------------
@router.get("/habits/add", response_class=HTMLResponse)
def add_habit_page(request: Request, db: Session = Depends(get_db)):
    """Show the Add Habit form."""
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "habit_form.html",
        {"request": request, "categories": categories, "mode": "add"}
    )


@router.post("/habits/add")
def add_habit(
    request: Request,
    name: str = Form(...),
    category_id: int = Form(...),
    difficulty: str = Form(...),
    frequency_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle Add Habit form submission."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    new_habit = Habit(
        user_id=user.id,
        name=name,
        category_id=category_id,
        difficulty=difficulty,
        frequency_type=frequency_type,
        start_date=date.today(),
    )
    db.add(new_habit)
    db.commit()

    # Award XP
    add_xp(db, user.id, 20)
    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)


# -----------------------------
# ✏️ Edit Habit
# -----------------------------
@router.get("/habits/edit/{habit_id}", response_class=HTMLResponse)
def edit_habit_page(request: Request, habit_id: int, db: Session = Depends(get_db)):
    """Show edit habit form."""
    habit = db.query(Habit).get(habit_id)
    categories = db.query(Category).all()

    if not habit:
        return RedirectResponse(url="/habits")

    return templates.TemplateResponse(
        "habit_form.html",
        {"request": request, "habit": habit, "categories": categories, "mode": "edit"}
    )


@router.post("/habits/edit/{habit_id}")
def edit_habit(
    request: Request,
    habit_id: int,
    name: str = Form(...),
    category_id: int = Form(...),
    difficulty: str = Form(...),
    frequency_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle habit edit submission."""
    habit = db.query(Habit).get(habit_id)
    if not habit:
        return RedirectResponse(url="/habits")

    habit.name = name
    habit.category_id = category_id
    habit.difficulty = difficulty
    habit.frequency_type = frequency_type
    db.commit()
    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)


# -----------------------------
# 🗑️ Delete Habit
# -----------------------------
@router.get("/habits/delete/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """Delete a habit permanently."""
    habit = db.query(Habit).get(habit_id)
    if habit:
        db.delete(habit)
        db.commit()
    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)


# -----------------------------
# ✅ Mark Habit as Done (Dynamic Button)
# -----------------------------
@router.post("/habits/{habit_id}/complete")
def complete_habit(habit_id: int, request: Request, db: Session = Depends(get_db)):
    """Log today's completion for a habit."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()

    existing = (
        db.query(HabitEntry)
        .filter(HabitEntry.user_id == user.id, HabitEntry.habit_id == habit_id, HabitEntry.entry_date == today)
        .first()
    )

    # Prevent double completion
    if not existing:
        entry = HabitEntry(user_id=user.id, habit_id=habit_id, entry_date=today)
        db.add(entry)
        db.commit()
        add_xp(db, user.id, 10)

    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)
