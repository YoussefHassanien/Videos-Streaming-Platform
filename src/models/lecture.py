from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.configs.database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    course_id: Mapped[str] = mapped_column(String(36),
                                           ForeignKey("courses.id",
                                                      ondelete="CASCADE"),
                                           nullable=False,
                                           index=True)
    asset_id: Mapped[str] = mapped_column(String(),
                                          nullable=False,
                                          unique=True)
    playback_id: Mapped[str] = mapped_column(String(),
                                             nullable=False,
                                             unique=True)
    url: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(200), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),
                                                 onupdate=func.now(),
                                                 nullable=True)

    # Reverse relationship - enables lecture.course access
    course = relationship("Course", back_populates="lectures")

    __table_args__ = (
        CheckConstraint("duration > 0",
                        name="check_lecture_duration_positive"),
        CheckConstraint("length(trim(asset_id)) > 0",
                        name="check_asset_id_not_empty"),
        CheckConstraint("length(trim(playback_id)) > 0",
                        name="check_playback_id_not_empty"),
        CheckConstraint("length(trim(url)) > 0", name="check_url_not_empty"),
        CheckConstraint("length(trim(title)) > 0",
                        name="check_title_not_empty"),
        CheckConstraint("length(trim(description)) > 0",
                        name="check_description_not_empty"),
        CheckConstraint("length(trim(category)) > 0",
                        name="check_category_not_empty"),
        CheckConstraint("length(trim(subcategory)) > 0",
                        name="check_subcategory_not_empty"),
    )
