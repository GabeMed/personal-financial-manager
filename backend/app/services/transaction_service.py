from sqlalchemy.orm import Session
from backend.app.crud.crud_category import get_category
from backend.app.crud.crud_transaction import (
    get_transactions,
    get_transaction,
    create_transaction,
    update_transaction,
    delete_transaction,
)
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
)
from backend.app.models.transaction import Transaction
from backend.app.services.errors import NotFoundError


def _ensure_category_belongs_to_user(db: Session, user_id: int, category_id: int):
    # Without this check a user could attach transactions to another user's
    # category just by guessing its id.
    if get_category(db, user_id, category_id) is None:
        raise NotFoundError("Category not found")


def list_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 25):
    """* Returns the transactions stored by a User, newest first.
    * Limits to 25 transactions per page
    """
    return get_transactions(db, user_id, skip, limit)


def get_user_transaction(db: Session, user_id: int, transaction_id: int):
    """* Returns one of the User's transactions or raises NotFoundError."""
    transaction = get_transaction(db, user_id, transaction_id)
    if transaction is None:
        raise NotFoundError("Transaction not found")
    return transaction


def add_transaction(db: Session, user_id: int, transaction_in: TransactionCreate):
    """* Creates a new transaction"""
    _ensure_category_belongs_to_user(db, user_id, transaction_in.category_id)
    return create_transaction(db, user_id, transaction_in)


def modify_transaction(
    db: Session, transaction: Transaction, transaction_in: TransactionUpdate
):
    """* Updates an existing transaction (patch)."""
    if transaction_in.category_id is not None:
        _ensure_category_belongs_to_user(
            db, transaction.user_id, transaction_in.category_id
        )
    return update_transaction(db, transaction, transaction_in)


def remove_transaction(db: Session, transaction: Transaction):
    """* Deletes a existing transaction"""
    delete_transaction(db, transaction)
