from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ChallengeStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    expired = "expired"

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    target_days = Column(Integer, default=3, nullable=False)
    completed_days = Column(Integer, default=0, nullable=False)
    status = Column(Enum(ChallengeStatus), default=ChallengeStatus.pending)
    bonus_xp = Column(Integer, default=50)
    created_at = Column(DateTime, server_default=func.now())

    habit = relationship("Habit")
