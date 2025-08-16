from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.modules.instructor.courses.repository import CoursesRepository
from src.modules.instructor.courses.schemas import (LectureUploadRequest,
                                                    CreateCourseRequest,
                                                    CreateCourseResponse,
                                                    LectureUploadResponse)
from src.modules.instructor.courses.utils import MuxUtils
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes


class CoursesController:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CoursesRepository(db)
        self.mux_utils = MuxUtils()

    async def upload_lecture(
        self,
        video: UploadFile,
        video_data: LectureUploadRequest,
    ) -> LectureUploadResponse:
        """
        Handles the full lifecycle of uploading a lecture using MuxUtils for clean separation
        """
        # Validate file type
        if not video.content_type or not video.content_type.startswith(
                'video/'):
            raise AppError(ErrorCodes.BAD_REQUEST, "File must be a video")

        try:
            # Step 1: Create upload URL using utility function
            upload_url, upload_id = await self.mux_utils.create_upload_url()

            # Step 2: Upload video to Mux using utility function
            await self.mux_utils.upload_video_to_mux(upload_url, video)

            # Step 3: Wait for asset processing using utility function
            asset_id, duration = await self.mux_utils.wait_for_asset_processing(
                upload_id)

            # Step 4: Save lecture to the database
            lecture = self.repository.create_lecture(
                video_data=video_data,
                asset_id=asset_id,
                duration=duration,
            )

            # Step 5: Update the parent course
            self.repository.update_course_data(course_id=video_data.course_id,
                                               duration=duration)

            return LectureUploadResponse(id=lecture.id,
                                         title=lecture.title,
                                         description=lecture.description,
                                         asset_id=lecture.asset_id,
                                         duration=lecture.duration,
                                         category=lecture.category,
                                         subcategory=lecture.subcategory,
                                         course_id=lecture.course_id)

        except AppError:
            raise  # Re-raise AppErrors as-is
        except Exception as e:
            raise AppError(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"Unexpected error during lecture upload: {str(e)}")

    async def create_course(self, course_data: CreateCourseRequest,
                            instructor_id: str) -> CreateCourseResponse:
        try:
            db_course = self.repository.create_course(course_data,
                                                      instructor_id)

            return CreateCourseResponse(
                id=db_course.id,
                title=db_course.title,
                description=db_course.description,
                duration=db_course.duration,
                lectures_count=db_course.lectures_count,
                premium=db_course.premium)

        except Exception as e:
            if isinstance(e, AppError):
                raise e
            else:
                raise AppError(
                    ErrorCodes.INTERNAL_SERVER_ERROR,
                    f"Unexpected error during course creation: {str(e)}")
