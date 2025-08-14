from pydantic import BaseModel, EmailStr, Field, validator
from src.models.user import UserRole
from datetime import datetime
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length = 100, min_length = 1)
    last_name: str = Field(..., max_length = 100, min_length = 1)
    email: EmailStr = Field(..., max_length=256)
    password: str = Field(..., min_length=8, max_length=256)
    date_of_birth: datetime
    mobile_number: str = Field(..., max_length=15, min_length=10)
    role: UserRole

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise AppError(ErrorCodes.TOO_SHORT_PASSWORD)
        if not any(char.isdigit() for char in v):
            raise AppError(ErrorCodes.ONE_DIGIT_REQUIRED)
        if not any(char.isupper() for char in v):
            raise AppError(ErrorCodes.ONE_UPPERCASE_LETTER_REQUIRED)
        return v


class LoginResponse(BaseModel):
    token: str
    first_name: str
    last_name: str

class TokenData(BaseModel):
    sub: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str