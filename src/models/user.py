from sqlalchemy import Column, String, DateTime, Enum, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    # Reverse relationship - enables instructor.courses access
    courses = relationship("Course", back_populates="instructor")

    __table_args__ = (
        CheckConstraint(
            "length(trim(first_name)) > 0",
            name="check_first_name_not_empty"
        ),
        CheckConstraint(
            "length(trim(last_name)) > 0",
            name="check_last_name_not_empty"
        ),
        CheckConstraint(
            "length(trim(email)) > 0",
            name="check_email_not_empty"
        ),
        CheckConstraint(
            "length(password) >= 8",
            name="check_password_min_length"
        ),
        CheckConstraint(
            "date_of_birth < CURRENT_TIMESTAMP",
            name="check_date_of_birth_past"
        ),
        CheckConstraint(
            "length(mobile_number) >= 10",
            name="check_mobile_number_min_length"
        ),
    )