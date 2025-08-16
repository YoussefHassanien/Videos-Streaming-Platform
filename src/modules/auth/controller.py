from sqlalchemy.orm import Session
from src.modules.auth.repository import AuthRepository
from src.modules.auth.schemas import UserCreate, LoginResponse, LoginResponse, TokenData
from src.modules.auth.utils import create_token
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthController:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> LoginResponse:
        """
        Create a new user account
        
        Args:
            user_data: User creation data
            
        Returns:
            Login Response: Created user first and last names and the generated token
            
        Raises:
            AppError: If user creation fails
        """
        try:
            # Create user through repository
            db_user = self.repository.create_user(user_data)

            token_data = TokenData(
                sub=db_user.id,
                role=db_user.role.value
            )

            token = create_token(token_data)
            
            return LoginResponse(
                token=token,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
            )
            
        except AppError:
            # Re-raise known application errors
            raise
        except Exception as e:
            # Handle unexpected errors
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR, f"Unexpected error during user creation: {str(e)}")
    
    async def authenticate_user(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate user and return login response with token
        
        Args:
            email: User email
            password: User password
            
        Returns:
            LoginResponse: Contains access token and user data
        """
        # Get user by email
        user = self.repository.get_user_by_email(email)
        if not user:
            raise AppError(ErrorCodes.BAD_REQUEST, "Invalid email or password")
        
        # Verify password
        if not pwd_context.verify(password, user.password):
            raise AppError(ErrorCodes.BAD_REQUEST, "Invalid email or password")
        
        # Create token data
        token_data = TokenData(
            sub=user.id,
            role=user.role.value
        )
        
        # Generate access token
        token = create_token(token_data)
        
        
        return LoginResponse(
            token=token,
            first_name=user.first_name,
            last_name=user.last_name,
        )