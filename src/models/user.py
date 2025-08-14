from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from src.configs.database import Base
import enum

class UserRole(enum.Enum):
    INSTRUCTOR = "instructor"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    password = Column(String(256), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    mobile_number = Column(String(15), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())