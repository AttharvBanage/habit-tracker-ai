from datetime import date, timedelta
import random

def predict_habit_risk(habit_name, streak, completion_rate, difficulty):
    """
    Returns (risk_score, prediction_message)
    Lower score = higher risk
    """

    # --- Base probability factors ---
    base = completion_rate
    streak_boost = min(streak.current_streak if streak else 0, 30) * 1.5
    diff_penalty = {"easy": 0, "medium": -10, "hard": -20}.get(difficulty, -5)

    # Predictive probability (0–100)
    predicted = max(min(base + streak_boost + diff_penalty, 100), 0)

    # Add small randomness for realistic feel
    predicted += random.uniform(-5, 5)
    predicted = round(max(min(predicted, 100), 0), 1)

    # Message
    if predicted >= 80:
        msg = f"💪 {habit_name} is going strong — high consistency expected!"
    elif predicted >= 60:
        msg = f"⚡ {habit_name} may need slight attention tomorrow."
    elif predicted >= 40:
        msg = f"⚠️ {habit_name} at risk — try scheduling earlier in the day."
    else:
        msg = f"🚨 {habit_name} likely to be skipped — plan a smaller target."

    return predicted, msg
