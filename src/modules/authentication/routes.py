from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.configs.database import get_db
from src.modules.authentication.controller import AuthController
from src.modules.authentication.schemas import UserCreate, LoginResponse, UserLogin, LoginResponse
from src.errors.app_errors import AppError
from src.middlewares.authentication import is_authenticated
from src.models.user import User

router = APIRouter()

@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="Register a new user with email, password, and personal information"
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user account
    
    - **first_name**: User's first name (1-100 characters)
    - **last_name**: User's last name (1-100 characters)  
    - **email**: Valid email address (unique)
    - **password**: Password (min 8 characters, must contain digit and uppercase letter)
    - **date_of_birth**: User's date of birth
    - **mobile_number**: Mobile phone number (10-15 characters, unique)
    - **role**: User role (instructor or student)
    
    Returns the created user information (without password)
    """
    controller = AuthController(db)
    return controller.create_user(user_data)

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return access token"
)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and user information
    """
    controller = AuthController(db)
    return controller.authenticate_user(login_data.email, login_data.password)