from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.oauth2 import get_current_user
from backend.app.models.user import User
from backend.app.schemas.category import CategoryCreate, CategoryResponse
from backend.app.services.category_service import list_categories, add_category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/all", response_model=list[CategoryResponse])
def read_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_categories(db, current_user.id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_category(db, current_user.id, cat_in)
