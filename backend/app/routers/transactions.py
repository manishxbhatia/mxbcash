from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.transaction import TransactionCreate, TransactionUpdate, TransactionRead
from ..services import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    account_id: Optional[int] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return transaction_service.list_transactions(db, account_id, from_date, to_date, limit, offset)


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    return transaction_service.create_transaction(db, data)


@router.get("/{txn_id}", response_model=TransactionRead)
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    return transaction_service.get_transaction(db, txn_id)


@router.patch("/{txn_id}", response_model=TransactionRead)
def update_transaction(txn_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    return transaction_service.update_transaction(db, txn_id, data)


@router.delete("/{txn_id}", status_code=204)
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    transaction_service.delete_transaction(db, txn_id)
