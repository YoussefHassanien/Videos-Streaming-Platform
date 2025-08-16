from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, CheckConstraint, Float, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configs.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, index=True)
    instructor_id = Column(String(36),
                           ForeignKey("users.id", ondelete="CASCADE"),
                           nullable=False,
                           index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    duration = Column(Float, default=0, nullable=True)
    lectures_count = Column(Integer, default=0, nullable=False)
    premium = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Reverse relationship - enables courses.instructor access
    instructor = relationship("User", back_populates="courses")

    # Reverse relationship - enables courses.lectures access
    lectures = relationship("Lecture", back_populates="course")

    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0",
                        name="check_title_not_empty"),
        CheckConstraint("length(trim(description)) > 0",
                        name="check_description_not_empty"),

        # duration cannot be negative
        CheckConstraint("duration >= 0", name="check_duration_non_negative"),

        # lectures_count cannot be negative
        CheckConstraint("lectures_count >= 0",
                        name="check_lectures_count_non_negative"),

        # if one is > 0, the other cannot be 0
        CheckConstraint(
            "(duration = 0 AND lectures_count = 0) OR (duration > 0 AND lectures_count > 0)",
            name="check_duration_lectures_consistency"),
    )
