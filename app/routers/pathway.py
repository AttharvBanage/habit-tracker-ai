from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.habit import Habit
from app.routers.auth import get_current_user_from_cookie
from app.core.pathway_ai import generate_21_day_plan

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/pathway/{habit_id}", response_class=HTMLResponse)
def show_pathway(request: Request, habit_id: int, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    habit = db.query(Habit).filter_by(id=habit_id, user_id=user.id).first()
    if not habit:
        return RedirectResponse(url="/habits")
    plan = generate_21_day_plan(habit.name, habit.category.name if habit.category else "Health", habit.difficulty)
    return templates.TemplateResponse("pathway.html", {"request": request, "user": user, "habit": habit, "plan": plan})
