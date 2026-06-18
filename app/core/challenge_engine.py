from datetime import date, timedelta
from app.core.utils import compute_consistency_score
from app.core.predictor import predict_habit_risk
from app.models.streak import Streak
from app.models.entry import HabitEntry
from app.models.habit import Habit
from app.models.challenge import Challenge, ChallengeStatus

def _completion_rate_30(db, habit_id):
    today = date.today()
    start = today - timedelta(days=30)
    cnt = db.query(HabitEntry).filter(HabitEntry.habit_id==habit_id, HabitEntry.entry_date>=start).count()
    return (cnt / 30) * 100

def propose_challenge_for_habit(db, habit: Habit):
    # inputs
    streak = db.query(Streak).filter_by(habit_id=habit.id).first()
    comp = _completion_rate_30(db, habit.id)
    score = compute_consistency_score(streak, habit.difficulty, comp)
    prob, _msg = predict_habit_risk(habit.name, streak, comp, habit.difficulty)
    risk = 100 - prob

    # decide challenge
    today = date.today()
    end = today + timedelta(days=7)

    if risk >= 60 or score < 50:
        title = "3-Day Streak Restart"
        desc = "Win back momentum: complete this habit on any 3 days this week."
        target = 3
        bonus = 60
    elif risk >= 35 or score < 70:
        title = "5-Day Consistency Boost"
        desc = "Stay steady: complete the habit on 5 of the next 7 days."
        target = 5
        bonus = 90
    else:
        title = "7-Day Mastery Sprint"
        desc = "Push your limits: complete the habit every day this week."
        target = 7
        bonus = 140

    ch = Challenge(
        user_id=habit.user_id,
        habit_id=habit.id,
        title=title,
        description=desc,
        start_date=today,
        end_date=end,
        target_days=target,
        status=ChallengeStatus.pending,
        bonus_xp=bonus
    )
    return ch
