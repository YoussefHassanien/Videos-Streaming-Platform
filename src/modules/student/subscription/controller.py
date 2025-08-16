from sqlalchemy.orm import Session
from src.modules.student.subscription.repository import SubscriptionRepository
from src.modules.student.subscription.schemas import SubscriptionResponse
from src.modules.instructor.courses.schemas import LectureUploadResponse
from src.modules.instructor.courses.schemas import Page, CourseListItemResponse
import math
from typing import List


class SubscriptionController:
    """Controller for handling student subscription logic."""

    def __init__(self, db: Session):
        self.repository = SubscriptionRepository(db)

    async def subscribe_to_course(self, student_id: str,
                                  course_id: str) -> SubscriptionResponse:
        """
        Handles the business logic for a student subscribing to a course.
        """
        subscription = self.repository.subscribe_to_course(
            student_id, course_id)

        # The response model will automatically convert the ORM object
        # because `from_attributes = True` is set in the schema.
        return subscription

    async def get_my_subscriptions(self, student_id: str, page: int,
                                   size: int) -> Page[CourseListItemResponse]:
        """
        Gets a student's subscribed courses and formats them into a paginated response.
        """
        courses, total = self.repository.get_subscribed_courses(
            student_id, page, size)

        # The response model will automatically convert the ORM object
        # because `from_attributes = True` is set in the schema.
        response_courses = [
            CourseListItemResponse.model_validate(course) for course in courses
        ]

        return Page(items=response_courses,
                    total=total,
                    page=page,
                    size=size,
                    pages=math.ceil(total / size) if size > 0 else 0)

    async def get_course_lectures(
            self, student_id: str,
            course_id: str) -> List[LectureUploadResponse]:
        """
        Handles the business logic for fetching lectures of a subscribed course.
        """
        lectures = self.repository.get_lectures_for_subscribed_course(
            student_id, course_id)
        return lectures #type: ignore
