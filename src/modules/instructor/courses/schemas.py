from typing import Optional
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
    id: str = Field(..., description="Course unique identifier")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    duration: float = Field(...,
                            ge=0.0,
                            description="Course duration in hours")
    lectures_count: int = Field(..., ge=0, description="Number of lectures")
    premium: bool = Field(..., description="Is premium course")

    class Config:
        from_attributes = True


class LectureUploadResponse(BaseModel):
    id: str = Field(..., description="Lecture unique identifier")
    title: str = Field(..., description="Lecture title")
    description: str = Field(..., description="Lecture description")
    asset_id: str = Field(..., description="Mux asset identifier")
    duration: float = Field(None, description="Lecture duration in seconds")
    category: str = Field(..., description="Lecture category")
    subcategory: str = Field(..., description="Lecture subcategory")
    course_id: str = Field(..., description="Associated course ID")

    class Config:
        from_attributes = True
