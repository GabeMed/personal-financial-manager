from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.oauth2 import get_current_user
from backend.app.schemas.transaction import (
    SummaryResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from backend.app.services.summary_service import get_summary
from backend.app.services.transaction_service import (
    list_transactions,
    get_user_transaction,
    add_transaction,
    modify_transaction,
    remove_transaction,
)
from backend.app.models.user import User

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/all", response_model=list[TransactionResponse])
def read_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_transactions(db, current_user.id, skip, limit)


@router.post(
    "", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_transaction(db, current_user.id, transaction_in)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = get_user_transaction(db, current_user.id, transaction_id)
    return modify_transaction(db, transaction, transaction_in)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = get_user_transaction(db, current_user.id, transaction_id)
    remove_transaction(db, transaction)


@router.get("/summary", response_model=SummaryResponse)
def read_summary(
    start: date | None = Query(None),
    end: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_summary(db, current_user.id, start, end)
