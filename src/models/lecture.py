from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, CheckConstraint, Float, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.configs.database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(String(36), primary_key=True, index=True)
    course_id = Column(String(36),
                       ForeignKey("courses.id", ondelete="CASCADE"),
                       nullable=False,
                       index=True)
    asset_id = Column(String(), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    duration = Column(Float, nullable=True)
    category = Column(String(200), nullable=False)
    subcategory = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Reverse relationship - enables lecture.course access
    course = relationship("Course", back_populates="lectures")

    __table_args__ = (
        CheckConstraint("duration > 0",
                        name="check_lecture_duration_positive"),
        CheckConstraint("length(trim(asset_id)) > 0",
                        name="check_asset_id_not_empty"),
        CheckConstraint("length(trim(title)) > 0",
                        name="check_title_not_empty"),
        CheckConstraint("length(trim(description)) > 0",
                        name="check_description_not_empty"),
        CheckConstraint("length(trim(category)) > 0",
                        name="check_category_not_empty"),
        CheckConstraint("length(trim(subcategory)) > 0",
                        name="check_subcategory_not_empty"),
    )
