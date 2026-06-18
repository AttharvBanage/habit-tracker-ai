import random
from datetime import date, timedelta
from app.models.habit import Habit
from app.models.entry import HabitEntry
from app.models.streak import Streak
from app.core.utils import compute_consistency_score

MOTIVATION_QUOTES = [
    "Small steps lead to big changes 🌱",
    "Consistency beats intensity. Keep going! 💪",
    "You're doing amazing — one habit at a time ✨",
    "Momentum is building. Don't stop now! 🚀",
    "Discipline is the bridge between goals and success 🌉",
]

def generate_ai_insight(db, user):
    """Generate smart coaching insights for a user's habits."""
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    if not habits:
        return {
            "summary": "No habits yet — your AI coach is waiting for your first move!",
            "insight": "Try adding a habit today to unlock personalized guidance.",
            "quote": random.choice(MOTIVATION_QUOTES)
        }

    active_habits = len(habits)
    total_entries = db.query(HabitEntry).filter(HabitEntry.user_id == user.id).count()
    last_7 = db.query(HabitEntry).filter(
        HabitEntry.user_id == user.id,
        HabitEntry.entry_date >= date.today() - timedelta(days=7)
    ).count()

    avg_consistency = 0
    for h in habits:
        streak = db.query(Streak).filter_by(habit_id=h.id).first()
        avg_consistency += compute_consistency_score(streak, h.difficulty, 70)
    avg_consistency = avg_consistency / active_habits if active_habits else 0

    # Smart AI insight messages
    if avg_consistency > 85:
        ai_msg = "🔥 You're on fire! Your consistency is elite level — keep that streak alive!"
        suggestion = "Try introducing a new 'growth' habit this week to challenge yourself."
    elif avg_consistency > 60:
        ai_msg = "⚡ Solid momentum — you’re improving every week!"
        suggestion = "Consider refining your schedule to boost morning habits."
    elif avg_consistency > 40:
        ai_msg = "🌙 You're finding your rhythm — stay patient and steady."
        suggestion = "Focus on one core habit for the next few days to regain flow."
    else:
        ai_msg = "💡 Try focusing on fewer habits to rebuild rhythm."
        suggestion = "Start small — aim to complete just one key habit daily."

    return {
        "summary": f"{active_habits} active habits · {total_entries} total logs · {last_7} entries this week",
        "insight": ai_msg,
        "suggestion": suggestion,
        "quote": random.choice(MOTIVATION_QUOTES)
    }
