from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class FrequencyEnum(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    custom = "custom"

class DifficultyEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.easy)
    frequency_type = Column(Enum(FrequencyEnum), default=FrequencyEnum.daily)
    custom_days = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="habits")
    user = relationship("User", back_populates="habits")

    entries = relationship("HabitEntry", back_populates="habit", cascade="all, delete")

