from fastapi import APIRouter, Depends, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from src.configs.database import get_db
from src.modules.instructor.courses.controller import CoursesController
from src.modules.instructor.courses.schemas import (CreateCourseRequest,
                                                    CreateCourseResponse,
                                                    LectureUploadResponse,
                                                    LectureUploadRequest)
from src.modules.auth.schemas import TokenData
from src.middlewares.auth import Auth
from src.models.user import UserRole

router = APIRouter()


@router.post(
    "/add-lecture",
    response_model=LectureUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Lecture",
    description="Upload a lecture video file with metadata (Instructors only)")
async def upload_Lecture(
        course_id: str = Form(...,
                              description="Course ID to associate video with"),
        title: str = Form(..., description="Lecture title"),
        description: str = Form(..., description="Lecture description"),
        category: str = Form(..., description="Lecture category"),
        subcategory: str = Form(..., description="Lecture subcategory"),
        lecture_file: UploadFile = File(..., description="Lecture video file"),
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(Auth(UserRole.INSTRUCTOR))):
    """
    Upload a Lecture file with metadata.

    - **lecture_file**: Lecture video file (mp4, avi, mov, etc.)
    - **title**: Lecture title
    - **description**:  Lecture description
    - **category**: Lecture category
    - **subcategory**: Lecture subcategory
    - **course_id**: - Associate Lecture with a specific course

    Requires instructor authentication.
    """
    lecture_data = LectureUploadRequest(course_id=course_id,
                                        title=title,
                                        description=description,
                                        category=category,
                                        subcategory=subcategory)
    controller = CoursesController(db)
    return await controller.upload_lecture(
        lecture_file,
        lecture_data,
    )


@router.post(
    "/",
    response_model=CreateCourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Course",
    description="Create an empty course to be linked with lectures later")
async def create_course(course_data: CreateCourseRequest,
                        db: Session = Depends(get_db),
                        current_user: TokenData = Depends(
                            Auth(UserRole.INSTRUCTOR))):
    """
    Create a new course.

    - **title**: Course title (required)
    - **description**: Course description (required)
    - **premium**: Whether the course is premium (optional, defaults to False)

    Creates an empty course that can later be populated with lectures/videos.
    The course will be associated with the authenticated instructor.

    Requires instructor authentication.
    
    Returns:
    - Course ID, title, description, duration, lecture count, and premium status
    """
    controller = CoursesController(db)
    return await controller.create_course(course_data, current_user.sub)
