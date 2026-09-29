from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.models.transaction import Transaction, TransactionType
from backend.app.models.user import User
from backend.app.schemas.transaction import TransactionCreate, TransactionUpdate


def signed_amount(amount: Decimal, type: TransactionType | str) -> Decimal:
    """Effect of a transaction on the balance: income adds, expense subtracts."""
    return amount if type == TransactionType.income else -amount


def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 25):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_transaction(
    db: Session, user_id: int, transaction_id: int
) -> Transaction | None:
    return (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
        .first()
    )


def create_transaction(db: Session, user_id: int, transaction_in: TransactionCreate):
    data = transaction_in.model_dump()
    transaction = Transaction(user_id=user_id, **data)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    user.balance += signed_amount(transaction.amount, transaction.type)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(
    db: Session, transaction: Transaction, transaction_in: TransactionUpdate
):
    # Capture the old effect on the balance *before* applying the patch, so
    # that changing the type (income <-> expense), the amount, or both is
    # reflected correctly. Fields omitted from the PATCH keep their value.
    old_effect = signed_amount(transaction.amount, transaction.type)

    update_data = transaction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    new_effect = signed_amount(transaction.amount, transaction.type)
    transaction.user.balance += new_effect - old_effect
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction):
    transaction.user.balance -= signed_amount(transaction.amount, transaction.type)
    db.delete(transaction)
    db.commit()
