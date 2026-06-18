from sqlalchemy import Column, Integer, Date, ForeignKey
from app.core.database import Base

class Streak(Base):
    __tablename__ = "streaks"
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_date = Column(Date)
