from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session
from src.configs.database import get_db
from src.modules.student.subscription.controller import SubscriptionController
from src.modules.student.subscription.schemas import SubscriptionRequest, SubscriptionResponse
from src.modules.instructor.courses.schemas import Page, CourseListItemResponse, LectureUploadResponse
from src.modules.auth.schemas import TokenData
from src.middlewares.auth import Auth
from src.models.user import UserRole
from typing import List
from src.configs.limiter import limiter

router = APIRouter()


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe to a Course",
    description="Allows an authenticated student to subscribe to a course.")
@limiter.limit("50/minute")
async def subscribe_to_course(request_body: SubscriptionRequest,
                              request: Request,
                              db: Session = Depends(get_db),
                              current_user: TokenData = Depends(
                                  Auth(UserRole.STUDENT))):
    """
    Subscribes the currently authenticated student to the specified course.
    
    - **course_id**: The ID of the course to subscribe to.
    
    This endpoint is only accessible by users with the 'STUDENT' role.
    """
    controller = SubscriptionController(db)
    return await controller.subscribe_to_course(
        student_id=current_user.sub, course_id=request_body.course_id)


@router.get(
    "/my-courses/{course_id}/lectures",
    response_model=List[LectureUploadResponse],
    summary="Get Lectures for a Subscribed Course",
    description=
    "Fetches all lectures for a specific course that the authenticated student is subscribed to."
)
@limiter.limit("50/minute")
async def get_subscribed_course_lectures(
        request: Request,
        course_id: str,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(Auth(UserRole.STUDENT)),
):
    controller = SubscriptionController(db)
    return await controller.get_course_lectures(student_id=current_user.sub,
                                                course_id=course_id)


@router.get(
    "/my-courses",
    response_model=Page[CourseListItemResponse],
    summary="Get My Subscribed Courses",
    description=
    "Fetches a paginated list of courses the authenticated student is subscribed to."
)
@limiter.limit("50/minute")
async def get_my_subscribed_courses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(Auth(UserRole.STUDENT)),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    size: int = Query(10,
                      ge=1,
                      le=100,
                      description="Number of courses per page")):
    controller = SubscriptionController(db)
    return await controller.get_my_subscriptions(student_id=current_user.sub,
                                                 page=page,
                                                 size=size)
