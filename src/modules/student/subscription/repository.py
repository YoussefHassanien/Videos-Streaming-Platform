from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from src.models.subscription import Subscription
from src.models.course import Course
from src.models.lecture import Lecture
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
import uuid
from typing import List


class SubscriptionRepository:
    """Repository for subscription-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def subscribe_to_course(self, student_id: str,
                            course_id: str) -> Subscription:
        """
        Creates a subscription record in the database for a student and a course.
        """
        # 1. Check if the course exists
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise AppError(ErrorCodes.NOT_FOUND, "Course not found.")

        # 2. Check if the student is already subscribed
        existing_subscription = self.db.query(Subscription).filter(
            Subscription.student_id == student_id,
            Subscription.course_id == course_id).first()

        if existing_subscription:
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "You are already subscribed to this course.")

        # 3. Create the new subscription
        new_subscription = Subscription(id=str(uuid.uuid4()),
                                        student_id=student_id,
                                        course_id=course_id)
        try:
            self.db.add(new_subscription)
            self.db.commit()
            self.db.refresh(new_subscription)
            return new_subscription
        except IntegrityError:
            # This is a fallback in case of a race condition
            # The unique constraint in the model will raise this error
            self.db.rollback()
            raise AppError(
                ErrorCodes.BAD_REQUEST,
                "Subscription failed. You may already be subscribed.")
        except Exception as e:
            self.db.rollback()
            raise AppError(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"Could not process subscription due to an unexpected error: {e}"
            )

    def get_subscribed_courses(self, student_id: str, page: int,
                               size: int) -> tuple[list[Course], int]:
        """
        Fetches all courses a student is subscribed to, with pagination.
        """
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        # First, get the total count of subscribed courses for pagination
        total = self.db.query(Subscription).filter(
            Subscription.student_id == student_id).count()

        # Then, get the paginated list of courses by joining through the subscription table
        courses = self.db.query(Course).join(Subscription).filter(
            Subscription.student_id == student_id).options(
                joinedload(
                    Course.instructor)  # Eager load to prevent N+1 queries
            ).offset((page - 1) * size).limit(size).all()

        return courses, total

    def get_lectures_for_subscribed_course(self, student_id: str,
                                           course_id: str) -> List[Lecture]:
        """
        Verifies a student's subscription and fetches all lectures for that course.
        """
        print(f"Course id: {course_id}, Student id: {student_id}")

        # 1. Verify that the student is subscribed to the course.
        subscription = self.db.query(Subscription).filter(
            Subscription.student_id == student_id,
            Subscription.course_id == course_id).first()

        if not subscription:
            raise AppError(
                ErrorCodes.PERMISSION_NOT_GRANTED,
                "Access denied. You are not subscribed to this course.")

        # 2. If subscribed, fetch all lectures associated with the course.
        lectures = self.db.query(Lecture).filter(
            Lecture.course_id == course_id).order_by(Lecture.created_at).all()

        return lectures
