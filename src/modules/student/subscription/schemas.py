from pydantic import BaseModel, Field
from datetime import datetime


class SubscriptionRequest(BaseModel):
    """Schema for a student's request to subscribe to a course."""
    course_id: str = Field(...,
                           description="The unique ID of the course to subscribe to.")


class SubscriptionResponse(BaseModel):
    """Schema for the response after a successful subscription."""
    id: str
    student_id: str
    course_id: str
    created_at: datetime

    class Config:
        from_attributes = True