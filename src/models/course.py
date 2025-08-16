from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, Float, Integer, Boolean, Column
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.configs.database import Base
from typing import Optional, List
from src.models.subscription import Subscription


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    instructor_id: Mapped[str] = mapped_column(String(36),
                                               ForeignKey("users.id"),
                                               nullable=False,
                                               index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lectures_count: Mapped[int] = mapped_column(Integer,
                                                nullable=False,
                                                default=0)
    premium: Mapped[bool] = mapped_column(Boolean,
                                          nullable=False,
                                          default=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now())

    # Reverse relationship - enables courses.instructor access
    instructor = relationship("User", back_populates="courses")

    # Reverse relationship - enables courses.lectures access
    lectures = relationship("Lecture", back_populates="course")

    # Reverse relationship - enables course.subscriptions access
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="course")

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
