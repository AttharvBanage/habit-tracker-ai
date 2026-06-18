def compute_consistency_score(streak, difficulty, completion_rate):
    if not streak:
        return 0

    # normalize streaks
    streak_factor = min(streak.current_streak / 30, 1.0) * 40
    best_factor = min(streak.best_streak / 60, 1.0) * 20

    # difficulty weighting
    diff_weight = {
        "easy": 0.8,
        "medium": 1.0,
        "hard": 1.2
    }
    diff_factor = diff_weight.get(difficulty, 1.0) * 20

    # completion contribution
    completion_factor = (completion_rate / 100) * 20

    total = streak_factor + best_factor + diff_factor + completion_factor
    return round(min(total, 100), 2)
