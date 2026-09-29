from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.crud import crud_user
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.core import oauth2

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_user_by_username(db, user.username):
        raise HTTPException(400, "Username already registered")
    if crud_user.get_user_by_email(db, user.email):
        raise HTTPException(400, "Email already registered")
    new_user = crud_user.create_user(db, user)
    return new_user


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(oauth2.get_current_user),
):
    return current_user
