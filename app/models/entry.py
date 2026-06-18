from sqlalchemy import Column, Integer, Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class MoodEnum(str, enum.Enum):
    very_low = "very_low"
    low = "low"
    neutral = "neutral"
    high = "high"
    very_high = "very_high"

class EntryVia(str, enum.Enum):
    manual = "manual"
    voice = "voice"
    image = "image"
    auto = "auto"

class HabitEntry(Base):
    __tablename__ = "habit_entries"

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    entry_date = Column(Date, nullable=False)
    count = Column(Integer, default=1)
    completed_at = Column(DateTime, server_default=func.now())
    mood = Column(Enum(MoodEnum), default=MoodEnum.neutral)
    proof_image_url = Column(String(255))
    via = Column(Enum(EntryVia), default=EntryVia.manual)

    habit = relationship("Habit", back_populates="entries")
