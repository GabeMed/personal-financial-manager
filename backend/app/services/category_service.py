from sqlalchemy.orm import Session
from backend.app.crud.crud_category import (
    get_categories,
    get_category_by_name,
    create_category,
)
from backend.app.schemas.category import CategoryCreate
from backend.app.services.errors import ConflictError


def list_categories(db: Session, user_id: int):
    """* Returns all the categories defined by a User"""
    return get_categories(db, user_id)


def add_category(db: Session, user_id: int, category_in: CategoryCreate):
    """* Creates a new category.
    * Links this new category to a User.
    * Category names are unique per user (case-insensitive).
    """
    if get_category_by_name(db, user_id, category_in.name):
        raise ConflictError(f"Category '{category_in.name}' already exists")
    return create_category(db, user_id, category_in.name)
