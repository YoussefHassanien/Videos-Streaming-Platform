import asyncio
import math
from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.modules.instructor.courses.repository import CoursesRepository
from src.modules.instructor.courses.schemas import (
    CourseListItemResponse, LectureUploadRequest, CreateCourseRequest, CreateCourseResponse,
    LectureUploadResponse, BatchLectureUploadRequest,
    BatchLectureUploadResponse, LectureUploadResult, Page)
from src.modules.instructor.courses.utils import MuxUtils
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from typing import List


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
            # check if the course is premium
            course = self.repository.find_course_by_id(video_data.course_id)

            # Step 1: Create upload URL using utility function
            upload_url, upload_id = await self.mux_utils.create_upload_url(
                course.premium)

            # Step 2: Upload video to Mux using utility function
            await self.mux_utils.upload_video_to_mux(upload_url, video)

            # Step 3: Wait for asset processing using utility function
            asset_id, playback_id, duration = await self.mux_utils.wait_for_asset_processing(
                upload_id)

            # Step 4: Generate playback url
            url = self.mux_utils.generate_playback_url(course.premium,
                                                       playback_id)

            # Step 5: Save lecture to the database
            lecture = self.repository.create_lecture(
                video_data=video_data,
                asset_id=asset_id,
                playback_id=playback_id,
                url=url,
                duration=duration,
            )

            # Step 6: Update the parent course
            self.repository.update_course_data(course_id=video_data.course_id,
                                               duration=duration)

            return LectureUploadResponse(id=lecture.id,
                                         title=lecture.title,
                                         description=lecture.description,
                                         asset_id=lecture.asset_id,
                                         playback_id=lecture.playback_id,
                                         url=lecture.url,
                                         duration=duration,
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

    async def upload_lectures_batch(
        self,
        videos: List[UploadFile],
        videos_data: BatchLectureUploadRequest,
    ) -> BatchLectureUploadResponse:
        """
        Handles batch upload of multiple lectures concurrently.
        """
        # Validate that number of videos matches lecture data
        if len(videos) != len(videos_data.lectures):
            raise AppError(
                ErrorCodes.BAD_REQUEST,
                f"Number of videos ({len(videos)}) must match number of lecture data ({len(videos_data.lectures)})"
            )

        # Validate all files are videos
        for i, video in enumerate(videos):
            if not video.content_type or not video.content_type.startswith(
                    'video/'):
                raise AppError(
                    ErrorCodes.BAD_REQUEST,
                    f"File {i+1} ({video.filename}) must be a video")

        # Create a list of tasks to run concurrently
        tasks = [
            self.upload_lecture(video, lecture_data)
            for video, lecture_data in zip(videos, videos_data.lectures)
        ]

        # Run all upload tasks concurrently and get results
        # return_exceptions=True ensures that if one task fails, the others continue
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process the results to build the final response
        processed_results: List[LectureUploadResult] = []
        successful_uploads = 0
        failed_uploads = 0

        for i, result in enumerate(results):
            video_filename = videos[i].filename or f"video_{i+1}"
            if isinstance(result, Exception):
                # This was a failed upload
                failed_uploads += 1
                processed_results.append(
                    LectureUploadResult(success=False,
                                        lecture=None,
                                        error=str(result),
                                        video_filename=video_filename))
            else:
                # This was a successful upload
                successful_uploads += 1
                processed_results.append(
                    LectureUploadResult(success=True,
                                        lecture=result,
                                        error=None,
                                        video_filename=video_filename))

        return BatchLectureUploadResponse(
            total_videos=len(videos),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            results=processed_results,
            course_id=videos_data.course_id)

    async def get_all_courses(self, page: int,
                              size: int) -> Page[CourseListItemResponse]:
        """Gets all courses and formats them into a paginated response."""
        courses, total = self.repository.get_all_courses(page, size)
        
        # Transform Course objects to CourseListItemResponse objects
        course_responses = [
            CourseListItemResponse(
                id=course.id,
                title=course.title,
                description=course.description,
                duration=course.duration,
                lectures_count=course.lectures_count,
                premium=course.premium,
                instructor=course.instructor
            ) for course in courses
        ]

        return Page(items=course_responses,
                    total=total,
                    page=page,
                    size=size,
                    pages=math.ceil(total / size) if size > 0 else 0)
