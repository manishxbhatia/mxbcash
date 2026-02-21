from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.transaction import Transaction, Split
from ..schemas.transaction import TransactionCreate, TransactionUpdate


def _check_zero_sum(splits: list) -> None:
    total = sum(s.value_minor for s in splits)
    if total != 0:
        raise HTTPException(
            status_code=422,
            detail=f"Splits do not sum to zero: sum(value_minor) = {total}",
        )


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    if len(data.splits) < 2:
        raise HTTPException(status_code=422, detail="A transaction requires at least 2 splits")

    # Validate zero-sum before creating anything
    total = sum(s.value_minor for s in data.splits)
    if total != 0:
        raise HTTPException(
            status_code=422,
            detail=f"Splits do not sum to zero: sum(value_minor) = {total}",
        )

    txn = Transaction(
        date=data.date,
        description=data.description,
        notes=data.notes,
        import_ref=data.import_ref,
        currency_id=data.currency_id,
    )
    db.add(txn)
    db.flush()

    for s in data.splits:
        split = Split(
            transaction_id=txn.id,
            account_id=s.account_id,
            value_minor=s.value_minor,
            quantity_minor=s.quantity_minor,
            memo=s.memo,
            reconciled=s.reconciled,
        )
        db.add(split)

    db.commit()
    db.refresh(txn)
    return txn


def get_transaction(db: Session, txn_id: int) -> Transaction:
    txn = db.get(Transaction, txn_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


def list_transactions(
    db: Session,
    account_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Transaction]:
    q = db.query(Transaction)
    if account_id is not None:
        q = q.join(Split, Transaction.id == Split.transaction_id).filter(
            Split.account_id == account_id
        )
    if from_date:
        q = q.filter(Transaction.date >= from_date)
    if to_date:
        q = q.filter(Transaction.date <= to_date)
    return q.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(offset).limit(limit).all()


def update_transaction(db: Session, txn_id: int, data: TransactionUpdate) -> Transaction:
    txn = get_transaction(db, txn_id)

    if data.date is not None:
        txn.date = data.date
    if data.description is not None:
        txn.description = data.description
    if data.notes is not None:
        txn.notes = data.notes
    if data.currency_id is not None:
        txn.currency_id = data.currency_id

    if data.splits is not None:
        total = sum(s.value_minor for s in data.splits)
        if total != 0:
            raise HTTPException(
                status_code=422,
                detail=f"Splits do not sum to zero: sum(value_minor) = {total}",
            )
        # Replace all splits
        for split in txn.splits:
            db.delete(split)
        db.flush()
        for s in data.splits:
            split = Split(
                transaction_id=txn.id,
                account_id=s.account_id,
                value_minor=s.value_minor,
                quantity_minor=s.quantity_minor,
                memo=s.memo,
                reconciled=s.reconciled,
            )
            db.add(split)

    db.commit()
    db.refresh(txn)
    return txn


def delete_transaction(db: Session, txn_id: int) -> None:
    txn = get_transaction(db, txn_id)
    db.delete(txn)
    db.commit()
