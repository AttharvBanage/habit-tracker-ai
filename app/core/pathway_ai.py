import random

def generate_21_day_plan(habit_name, category, difficulty):
    """Generate a dynamic 21-day AI habit improvement plan"""
    templates = {
        "Fitness": [
            "Warm-up 5 min longer",
            "Add 1 extra set to your routine",
            "Track hydration after workout",
            "Take a walk instead of scrolling",
            "Try a new stretch routine",
            "Rest and reflect on progress",
            "Increase intensity slightly",
            "Journal energy levels post workout",
            "Adjust form with video tutorial",
            "Reward yourself after completing",
        ],
        "Learning": [
            "Summarize what you read today",
            "Teach someone a concept you learned",
            "Replace music with podcast once",
            "Try studying at a different time",
            "Highlight 3 key takeaways",
            "Write a small blog summary",
            "Use Pomodoro (25-min focus)",
            "Review old notes for retention",
            "Create flashcards for topics",
            "Test yourself for fun",
        ],
        "Health": [
            "Drink a glass of water after waking",
            "Avoid screen before sleep",
            "Meditate 5 minutes",
            "Eat one fruit today",
            "Add greens to a meal",
            "Take a deep breathing break",
            "Walk for 10 minutes after meals",
            "Replace sugar snack with fruit",
            "Journal sleep quality",
            "Try sleeping 15 min earlier",
        ]
    }

    base = templates.get(category, templates["Health"])
    plan = []
    diff_factor = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 2)

    for day in range(1, 22):
        task = random.choice(base)
        effort = "🌿 Light" if diff_factor == 1 else "🔥 Medium" if diff_factor == 2 else "💪 Intense"
        plan.append({
            "day": day,
            "task": task,
            "effort": effort,
            "motivation": random.choice([
                "You’re doing amazing!",
                "Keep momentum alive.",
                "Every small win counts.",
                "Consistency > intensity.",
                "You got this 🔥"
            ])
        })
    return plan
