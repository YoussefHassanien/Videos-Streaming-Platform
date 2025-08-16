from fastapi import APIRouter, Depends, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from src.configs.database import get_db
from src.modules.instructor.courses.controller import CoursesController
from src.modules.instructor.courses.schemas import (CreateCourseRequest,
                                                    CreateCourseResponse,
                                                    LectureUploadResponse,
                                                    LectureUploadRequest,
                                                    BatchLectureUploadRequest,
                                                    BatchLectureUploadResponse)
from src.modules.auth.schemas import TokenData
from src.middlewares.auth import Auth
from src.models.user import UserRole
from typing import List
import json

router = APIRouter()


@router.post("/add-lectures-batch",
             response_model=BatchLectureUploadResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Upload Multiple Lectures",
             description="Upload multiple video lectures to a course in batch")
async def upload_lectures_batch(
        lectures_files: List[UploadFile] = File(
            ...,
            description=
            "List of video files to upload (exactly 2 files required)",
            min_length=2,
            max_length=2),
        lectures_data: str = Form(
            ...,
            description=
            "JSON string containing list of 2 LectureUploadRequest objects"),
        course_id: str = Form(...,
                              description="Course ID to associate video with"),
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(Auth(UserRole.INSTRUCTOR))):
    """
    Upload exactly 2 lectures to courses in batch.
    
    - **lectures_files**: List of exactly 2 video files
    - **lectures_data**: JSON string containing list of 2 LectureUploadRequest objects
    - **course_id**: - Associate Lectures with a specific course
    
    The lectures_data should be a JSON string with the following structure:
    ```json
    [
        {
            "course_id": "course-uuid-1",
            "title": "Lecture 1",
            "description": "Description 1",
            "category": "Category 1",
            "subcategory": "Subcategory 1"
        },
        {
            "course_id": "course-uuid-2",
            "title": "Lecture 2", 
            "description": "Description 2",
            "category": "Category 2",
            "subcategory": "Subcategory 2"
        }
    ]
    ```
    
    **Requirements:**
    - Exactly 2 video files required
    - Exactly 2 LectureUploadRequest objects required
    - Each video file must be in supported video format
    - Each lecture can be uploaded to different courses
    """

    # ✅ Validate exactly 2 files
    if len(lectures_files) != 2:
        raise AppError(
            ErrorCodes.BAD_REQUEST,
            f"Exactly 2 video files required, got {len(lectures_files)}")

    # ✅ Parse and validate lectures data as list of LectureUploadRequest
    try:
        try:
            lectures_data_parsed = json.loads(lectures_data)
        except json.JSONDecodeError as e:
            raise AppError(ErrorCodes.BAD_REQUEST,
                           f"Invalid JSON format in lectures_data: {str(e)}")

        # Validate it's a list
        if not isinstance(lectures_data_parsed, list):
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "lectures_data must be a JSON array")

        # Validate exactly 2 objects
        if len(lectures_data_parsed) != 2:
            raise AppError(
                ErrorCodes.BAD_REQUEST,
                f"Exactly 2 LectureUploadRequest objects required, got {len(lectures_data_parsed)}"
            )

        # ✅ Validate and convert to LectureUploadRequest objects
        lecture_requests = []
        for i, lecture_data in enumerate(lectures_data_parsed):
            try:
                # Validate required fields
                required_fields = [
                    'course_id', 'title', 'description', 'category',
                    'subcategory'
                ]
                for field in required_fields:
                    if field not in lecture_data or not lecture_data[field]:
                        raise AppError(
                            ErrorCodes.BAD_REQUEST,
                            f"Missing required field '{field}' in lecture {i+1}"
                        )

                lecture_request = LectureUploadRequest(**lecture_data)
                lecture_requests.append(lecture_request)

            except TypeError as e:
                raise AppError(
                    ErrorCodes.BAD_REQUEST,
                    f"Invalid data format for lecture {i+1}: {str(e)}")

        # ✅ Validate video files
        for i, video_file in enumerate(lectures_files):
            if not video_file.content_type or not video_file.content_type.startswith(
                    'video/'):
                raise AppError(
                    ErrorCodes.BAD_REQUEST,
                    f"File {i+1} ({video_file.filename}) must be a video file")

        # ✅ Call controller
        controller = CoursesController(db)
        batch_request = BatchLectureUploadRequest(lectures=lecture_requests,
                                                  course_id=course_id)
        return await controller.upload_lectures_batch(lectures_files,
                                                      batch_request)

    except AppError:
        raise
    except Exception as e:
        raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                       f"Unexpected error in batch upload: {str(e)}")


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

    Creates an empty course that can later be populated with lectures/lectures_files.
    The course will be associated with the authenticated instructor.

    Requires instructor authentication.
    
    Returns:
    - Course ID, title, description, duration, lecture count, and premium status
    """
    controller = CoursesController(db)
    return await controller.create_course(course_data, current_user.sub)
