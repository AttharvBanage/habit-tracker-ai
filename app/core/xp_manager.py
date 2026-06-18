from math import floor
from sqlalchemy.orm import Session
from sqlalchemy import text

def ensure_user_xp(db: Session, user_id: int):
    db.execute(
        text("INSERT IGNORE INTO user_xp (user_id, xp, level) VALUES (:uid, 0, 1)"),
        {"uid": user_id}
    )
    db.commit()


def add_xp(db: Session, user_id: int, amount: int):
    ensure_user_xp(db, user_id)
    db.execute(
        text("UPDATE user_xp SET xp = xp + :amt WHERE user_id = :uid"),
        {"amt": amount, "uid": user_id}
    )
    db.commit()
    update_level(db, user_id)

def update_level(db: Session, user_id: int):
    row = db.execute(
        text("SELECT xp FROM user_xp WHERE user_id = :uid"),
        {"uid": user_id}
    ).fetchone()
    if row:
        xp = row[0]
        level = max(1, floor(xp / 200) + 1)
        db.execute(
            text("UPDATE user_xp SET level = :lvl WHERE user_id = :uid"),
            {"lvl": level, "uid": user_id}
        )
        db.commit()

def get_xp_data(db: Session, user_id: int):
    data = db.execute(
        text("SELECT xp, level FROM user_xp WHERE user_id = :uid"),
        {"uid": user_id}
    ).fetchone()
    return {"xp": data[0], "level": data[1]} if data else {"xp": 0, "level": 1}
