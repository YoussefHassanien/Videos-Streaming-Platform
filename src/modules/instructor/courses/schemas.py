from typing import Optional, List
from pydantic import BaseModel, Field


class LectureUploadRequest(BaseModel):
    course_id: str = Field(...,
                           min_length=1,
                           max_length=36,
                           description="Course ID to associate video with")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=200)
    subcategory: str = Field(..., min_length=1, max_length=200)


class CreateCourseRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    premium: Optional[bool] = False


class CreateCourseResponse(BaseModel):
    id: str
    title: str
    description: str
    duration: float
    lectures_count: int
    premium: bool


class LectureUploadResponse(BaseModel):
    id: str
    title: str
    description: str
    asset_id: str
    playback_id: str
    url: str
    duration: float
    category: str
    subcategory: str
    course_id: str


class LectureUploadResult(BaseModel):
    success: bool = Field(
        ...,
        description="Indicates if the individual lecture upload was successful."
    )
    lecture: Optional[LectureUploadResponse] = Field(
        None, description="The created lecture data if successful.")
    error: Optional[str] = Field(
        None, description="Error message if the upload failed.")
    video_filename: str = Field(
        ..., description="The original filename of the uploaded video.")


class BatchLectureUploadRequest(BaseModel):
    course_id: str = Field(...,
                           min_length=1,
                           max_length=36,
                           description="Course ID to associate videos with")
    lectures: List[LectureUploadRequest] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="List of lecture data (max 2)")


class BatchLectureUploadResponse(BaseModel):
    total_videos: int = Field(
        ..., description="The total number of videos processed in the batch.")
    successful_uploads: int = Field(
        ...,
        description="The number of videos that were successfully uploaded.")
    failed_uploads: int = Field(
        ..., description="The number of videos that failed to upload.")
    results: List[LectureUploadResult] = Field(
        ...,
        description="A detailed list of results for each video in the batch.")
    course_id: str = Field(...,
                           description="The course ID to which the lectures")
