from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from src.configs.database import get_db
from src.modules.auth.controller import AuthController
from src.modules.auth.schemas import UserCreate, LoginResponse, UserLogin, LoginResponse
from src.configs.limiter import limiter

router = APIRouter()


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description=
    "Register a new user with email, password, and personal information")
@limiter.limit("5/minute")
async def create_user(user_data: UserCreate,
                      request: Request,
                      db: Session = Depends(get_db)):
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
    return await controller.create_user(user_data)


@router.post("/login",
             response_model=LoginResponse,
             status_code=status.HTTP_200_OK,
             summary="User login",
             description="Authenticate user and return access token")
@limiter.limit("10/minute")
async def login_user(login_data: UserLogin,
                     request: Request,
                     db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and user information
    """
    controller = AuthController(db)
    return await controller.authenticate_user(login_data.email,
                                              login_data.password)
