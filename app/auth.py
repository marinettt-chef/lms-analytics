from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User, Login, Enrollment

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(db: Session, login_id: str):
    """Verify user credentials"""
    login = db.query(Login).filter(Login.user_login_id == login_id).first()
    if login and login.user.user_state == "registered":
        return login.user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.user_id == user_id).first()
    return user

def is_instructor(user: User, db: Session) -> bool:
    """Check if user is an instructor"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == user.user_id,
        Enrollment.enrollment_type == "teacher"
    ).first()
    return enrollments is not None

def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.login.user_login_id == "admin"
