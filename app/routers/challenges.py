from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.routers.auth import get_current_user_from_cookie
from app.models import Habit, Challenge, ChallengeStatus
from app.core.challenge_engine import propose_challenge_for_habit
from app.core.xp_manager import add_xp, get_xp_data  # ✅ added
from sqlalchemy import text



router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------
# 🧠 Helper: Ensure XP table entry
# ---------------------------------
from sqlalchemy import text

def _ensure_user_xp(db, user_id):
    db.execute(text("""
        INSERT OR IGNORE INTO user_xp (user_id, xp, level)
        VALUES (:user_id, 0, 1)
    """), {"user_id": user_id})
    db.commit()




# ---------------------------------
# 🎯 View All Challenges
# ---------------------------------
@router.get("/challenges", response_class=HTMLResponse)
def view_challenges(request: Request, db: Session = Depends(get_db)):
    """Display all challenges for the logged-in user."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()

    # Expire old pending/active challenges
    db.query(Challenge).filter(
        Challenge.user_id == user.id,
        Challenge.status.in_([ChallengeStatus.pending, ChallengeStatus.active]),
        Challenge.end_date < today
    ).update({Challenge.status: ChallengeStatus.expired})
    db.commit()

    # Fetch user challenges, newest first
    challenges = (
        db.query(Challenge)
        .filter(Challenge.user_id == user.id)
        .order_by(Challenge.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "challenges.html",
        {"request": request, "user": user, "challenges": challenges}
    )


# ---------------------------------
# 🧩 Generate Weekly/Custom Challenges
# ---------------------------------
@router.post("/challenges/generate")
def generate_challenges(request: Request, db: Session = Depends(get_db)):
    """Generate new challenges for all active habits (no duplicates)."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    today = date.today()

    habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).all()

    for habit in habits:
        # Skip if a challenge already exists for this habit & week
        existing = db.query(Challenge).filter(
            Challenge.habit_id == habit.id,
            Challenge.user_id == user.id,
            Challenge.status.in_([ChallengeStatus.pending, ChallengeStatus.active]),
            Challenge.end_date >= today
        ).first()

        if existing:
            continue  # already has an ongoing challenge

        # Generate a new challenge dynamically using AI engine
        new_challenge = propose_challenge_for_habit(db, habit)
        db.add(new_challenge)

    db.commit()
    return RedirectResponse(url="/challenges", status_code=status.HTTP_302_FOUND)


# ---------------------------------
# ✅ Accept a Pending Challenge
# ---------------------------------
@router.post("/challenges/accept/{challenge_id}")
def accept_challenge(challenge_id: int, request: Request, db: Session = Depends(get_db)):
    """Mark a pending challenge as active."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.user_id == user.id
    ).first()

    if challenge and challenge.status == ChallengeStatus.pending:
        challenge.status = ChallengeStatus.active
        db.commit()

    return RedirectResponse(url="/challenges", status_code=status.HTTP_302_FOUND)


# ---------------------------------
# ---------------------------------
# 🏁 Mark Challenge Progress / Completion
# ---------------------------------
from sqlalchemy import text

# ---------------------------------
# 🏁 Mark Challenge Progress / Completion
# ---------------------------------
from app.core.xp_manager import add_xp  # adjust path as needed


@router.post("/challenges/mark/{challenge_id}")
def mark_challenge(challenge_id: int, request: Request, db: Session = Depends(get_db)):
    """Mark one day as completed for a challenge and handle XP rewards."""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.user_id == user.id
    ).first()

    # Skip invalid or already completed challenges
    if not challenge or challenge.status not in [ChallengeStatus.active, ChallengeStatus.pending]:
        return RedirectResponse(url="/challenges", status_code=status.HTTP_302_FOUND)

    # Activate pending challenge if needed
    if challenge.status == ChallengeStatus.pending:
        challenge.status = ChallengeStatus.active

    # Increment completed days safely
    challenge.completed_days = min(challenge.completed_days + 1, challenge.target_days)

    # If fully completed
    if challenge.completed_days >= challenge.target_days:
        challenge.status = ChallengeStatus.completed

        # ✅ Add XP reward using helper (handles creation + level update)
        add_xp(db, user.id, challenge.bonus_xp)

    db.commit()

    # Refresh XP data for UI update
    xp_data = get_xp_data(db, user.id)
    print(f"✅ Challenge completed! User {user.id} new XP: {xp_data['xp']}, Level: {xp_data['level']}")

    return RedirectResponse(url="/challenges", status_code=status.HTTP_302_FOUND)