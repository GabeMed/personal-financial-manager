from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.models.category import Category


def get_categories(db: Session, user_id: int):
    return (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.name)
        .all()
    )


def get_category(db: Session, user_id: int, category_id: int) -> Category | None:
    return (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )


def get_category_by_name(db: Session, user_id: int, name: str) -> Category | None:
    return (
        db.query(Category)
        .filter(Category.user_id == user_id, func.lower(Category.name) == name.lower())
        .first()
    )


def create_category(db: Session, user_id: int, name: str):
    category = Category(user_id=user_id, name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
