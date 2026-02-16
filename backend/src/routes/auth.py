"""Authentication routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.models.signal import UserCreate, UserLogin, Token
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# TODO: Implement authentication when database is ready
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        
    Returns:
        Success message
    """
    # TODO: Implement user registration
    logger.info(f"Registration requested for {user_data.email}")
    raise HTTPException(
        status_code=501,
        detail="User registration not yet implemented"
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return JWT token
    
    Args:
        form_data: OAuth2 password form data
        
    Returns:
        JWT access token
    """
    # TODO: Implement user login and JWT generation
    logger.info(f"Login requested for {form_data.username}")
    raise HTTPException(
        status_code=501,
        detail="User login not yet implemented"
    )
