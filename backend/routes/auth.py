from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from bson import ObjectId

from models.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from database import get_database
from config import get_settings
import bcrypt

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    db = get_database()
    user = await db.users.find_one({"_id": token_data.user_id})
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = get_database()

    # Check if email exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password_hash": get_password_hash(user.password),
        "created_at": datetime.utcnow()
    }

    result = await db.users.insert_one(user_dict)

    return UserResponse(
        id=result.inserted_id,
        username=user_dict["username"],
        email=user_dict["email"],
        created_at=user_dict["created_at"]
    )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    db = get_database()

    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["_id"]}
    )

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["_id"],
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )


@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users except current user"""
    db = get_database()
    users = []
    # Convert to list synchronously to handle in-memory DB
    all_users = await db.users.find({}).to_list(100)
    for user in all_users:
        if user["_id"] != current_user["_id"]:
            users.append(UserResponse(
                id=user["_id"],
                username=user["username"],
                email=user["email"],
                created_at=user["created_at"]
            ))
    return users
