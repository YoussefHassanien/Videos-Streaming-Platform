from sqlalchemy.orm import Session
from typing import Optional
from src.models.user import User
from src.modules.authentication.schemas import UserCreate
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_mobile(self, mobile_number: str) -> Optional[User]:
        """Get user by mobile number"""
        return self.db.query(User).filter(User.mobile_number == mobile_number).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise AppError(ErrorCodes.USER_ALREADY_EXISTS, "Email already registered")
        
        if self.get_user_by_mobile(user_data.mobile_number):
            raise AppError(ErrorCodes.USER_ALREADY_EXISTS, "Mobile number already registered")
        
        try:
            # Hash the password
            hashed_password = pwd_context.hash(user_data.password)
            
            # Create user instance
            db_user = User(
                id=str(uuid.uuid4()),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                password=hashed_password,
                date_of_birth=user_data.date_of_birth,
                mobile_number=user_data.mobile_number,
                role=user_data.role
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
            
        except Exception as e:
            self.db.rollback()
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to create user: {str(e)}")