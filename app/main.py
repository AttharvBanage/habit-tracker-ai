from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.database import Base, engine, get_db

# Routers
from app.routers import (
    auth,
    habit,
    progress,
    analytics,
    predict,
    pathway,
    challenges,
    coach,
    ai_insights,
    voice
)

# XP utilities
from app.core.xp_manager import get_xp_data
from app.routers.auth import get_current_user_from_cookie

# ✅ Create all DB tables
Base.metadata.create_all(bind=engine)

# ✅ Initialize app
app = FastAPI(title="Habit Tracker AI")

# ✅ Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ✅ Default route → redirect to /habits
@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/habits")


# ======================================================
# 🌟 GLOBAL XP MIDDLEWARE (injects user + xp_data everywhere)
# ======================================================
@app.middleware("http")
async def add_xp_data_to_context(request: Request, call_next):
    """
    Injects current user and XP data into every template render.
    This ensures the navbar always shows up-to-date XP and level.
    """
    try:
        db = next(get_db())
        user = get_current_user_from_cookie(request, db)
        if user:
            xp_data = get_xp_data(db, user.id)
            request.state.user = user
            request.state.xp_data = xp_data
        else:
            request.state.user = None
            request.state.xp_data = {"xp": 0, "level": 1}
    except Exception as e:
        print("⚠️ XP Middleware Error:", e)
        request.state.user = None
        request.state.xp_data = {"xp": 0, "level": 1}

    response = await call_next(request)
    return response


# ======================================================
# ✅ ROUTERS (no duplicates)
# ======================================================
app.include_router(auth.router)
app.include_router(habit.router)
app.include_router(progress.router)
app.include_router(analytics.router)
app.include_router(predict.router)
app.include_router(pathway.router)
app.include_router(challenges.router)
app.include_router(coach.router)
app.include_router(ai_insights.router)
app.include_router(voice.router)
