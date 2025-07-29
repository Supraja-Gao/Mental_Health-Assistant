# backend/auth.py

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from pydantic import BaseModel

from backend.models import User
from backend.database import get_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security settings
SECRET_KEY = "your-secret-key"  # ⚠️ Replace with a secure random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id:int

class TokenData(BaseModel):
    username: str | None = None

class RegisterInput(BaseModel):
    username: str
    email: str
    password: str

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user_obj = db.exec(select(User).where(User.username == username)).first()
    if not user_obj or not verify_password(password, user_obj.hashed_password):
        return None
    return user_obj



# Auth endpoints
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: RegisterInput, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"msg": "Registered successfully", "user_id": new_user.id}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_id": user.id  # ✅ send user_id back to frontend
}

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    credentials_ex = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_ex
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_ex

    user = session.exec(select(User).where(User.username == token_data.username)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/me", response_model=RegisterInput, summary="Get current user")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return RegisterInput(
        username=current_user.username,
        email=current_user.email,
        password="",  # do not return password
    ) 
    
