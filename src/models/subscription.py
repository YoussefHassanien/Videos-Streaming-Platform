from sqlalchemy import (String, DateTime, ForeignKey, UniqueConstraint)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.configs.database import Base
from typing import Optional


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(36),
                                            ForeignKey("users.id",
                                                       ondelete="CASCADE"),
                                            nullable=False)
    course_id: Mapped[str] = mapped_column(String(36),
                                           ForeignKey("courses.id",
                                                      ondelete="CASCADE"),
                                           nullable=False)

    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now())

    # Relationships to enable subscription.student and subscription.course
    student = relationship("User", back_populates="subscriptions")
    course = relationship("Course", back_populates="subscriptions")

    __table_args__ = (
        # Ensures a student can only subscribe to a course once
        UniqueConstraint('student_id', 'course_id',
                         name='_student_course_uc'), )
