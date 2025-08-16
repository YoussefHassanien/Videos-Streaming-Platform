from sqlalchemy.orm import Session
from src.models.lecture import Lecture
from src.models.course import Course
from src.models.user import User
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from .schemas import CreateCourseRequest, LectureUploadRequest
import uuid


class CoursesRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_lecture(
        self,
        video_data: LectureUploadRequest,
        asset_id: str,
        duration: float,
    ) -> Lecture:
        """Create a new video lecture record"""

        course = self.db.query(Course).filter(
            Course.id == video_data.course_id).first()
        if not course:
            raise AppError(ErrorCodes.NOT_FOUND, "Course not found!")

        video = Lecture(id=str(uuid.uuid4()),
                        course_id=video_data.course_id,
                        title=video_data.title,
                        description=video_data.description,
                        asset_id=asset_id,
                        category=video_data.category,
                        subcategory=video_data.subcategory,
                        duration=duration)

        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)

        return video

    def create_course(self, course_data: CreateCourseRequest,
                      instructor_id: str) -> Course:

        user = self.db.query(User).filter(User.id == instructor_id).first()

        if not user:
            raise AppError(ErrorCodes.NOT_FOUND, "User not found!")

        db_course = Course(id=str(uuid.uuid4()),
                           instructor_id=instructor_id,
                           title=course_data.title,
                           description=course_data.description,
                           premium=course_data.premium)

        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)

        return db_course

    def update_course_data(self, course_id: str, duration: float) -> Course:
        """
        Updates a course's total duration and increments its lectures count.

        Args:
            course_id: The ID of the course to update.
            duration: The duration of the new lecture to be added to the course total.

        Returns:
            The updated course object.

        Raises:
            AppError: If the course with the given ID is not found.
        """
        # Lock the course row for update to prevent race conditions
        course = self.db.query(Course).filter(
            Course.id == course_id).with_for_update().first()

        if not course:
            raise AppError(ErrorCodes.NOT_FOUND, "Course not found!")

        # Add the new lecture's duration to the course's total duration
        course.duration += duration

        # Increment the number of lectures in the course
        course.lectures_count += 1

        self.db.commit()
        self.db.refresh(course)

        return course
