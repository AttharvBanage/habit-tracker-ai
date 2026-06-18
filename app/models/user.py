from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base
from sqlalchemy.orm import relationship

# add this at the bottom inside User class:


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    habits = relationship("Habit", back_populates="user", cascade="all, delete")
