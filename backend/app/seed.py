"""Demo data so the app has something to show on first run.

Creates the user `demo` / `demo1234` with a few categories and two months of
transactions. Idempotent: does nothing if the demo user already exists.

    python -m backend.app.seed          # from the repository root
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.crud import crud_user
from backend.app.db.base import Base, SessionLocal, engine
from backend.app.schemas.category import CategoryCreate
from backend.app.schemas.transaction import TransactionCreate
from backend.app.schemas.user import UserCreate
from backend.app.services.category_service import add_category
from backend.app.services.transaction_service import add_transaction

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"

# (days ago, type, amount, category, description)
DEMO_TRANSACTIONS = [
    (58, "income", "6500.00", "Salary", "Monthly salary"),
    (56, "expense", "1800.00", "Rent", "Apartment rent"),
    (52, "expense", "412.35", "Groceries", "Supermarket"),
    (47, "expense", "96.90", "Transport", "Metro card top-up"),
    (41, "income", "1200.00", "Freelance", "Landing page project"),
    (38, "expense", "180.00", "Leisure", "Concert tickets"),
    (28, "income", "6500.00", "Salary", "Monthly salary"),
    (26, "expense", "1800.00", "Rent", "Apartment rent"),
    (21, "expense", "388.10", "Groceries", "Supermarket"),
    (15, "expense", "54.50", "Transport", "Ride to the airport"),
    (9, "expense", "129.90", "Leisure", "Dinner with friends"),
    (3, "expense", "236.75", "Groceries", "Farmers market"),
]


def seed_demo_data(db: Session) -> bool:
    """Returns True if data was created, False if it already existed."""
    if crud_user.get_user_by_username(db, DEMO_USERNAME):
        return False

    user = crud_user.create_user(
        db,
        UserCreate(
            username=DEMO_USERNAME, email="demo@example.com", password=DEMO_PASSWORD
        ),
    )
    categories = {}
    for name in sorted({t[3] for t in DEMO_TRANSACTIONS}):
        categories[name] = add_category(db, user.id, CategoryCreate(name=name))

    now = datetime.now(UTC)
    for days_ago, type_, amount, category, description in DEMO_TRANSACTIONS:
        add_transaction(
            db,
            user.id,
            TransactionCreate(
                type=type_,
                amount=Decimal(amount),
                description=description,
                date=now - timedelta(days=days_ago),
                category_id=categories[category].id,
            ),
        )
    return True


if __name__ == "__main__":
    import backend.app.models  # noqa: F401  (registers the ORM models)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        created = seed_demo_data(db)
    print("Demo data created." if created else "Demo user already exists.")
