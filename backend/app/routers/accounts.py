from typing import List, Union
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.account import AccountCreate, AccountUpdate, AccountRead, AccountTreeNode
from ..services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=Union[List[AccountRead], List[AccountTreeNode]])
def list_accounts(
    tree: bool = Query(False),
    db: Session = Depends(get_db),
):
    accounts = account_service.list_accounts(db)
    if tree:
        return account_service.build_tree(accounts)
    return accounts


@router.post("", response_model=AccountRead, status_code=201)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    return account_service.create_account(db, data)


@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return account_service.get_account(db, account_id)


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    return account_service.update_account(db, account_id, data)


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account_service.delete_account(db, account_id)


@router.get("/{account_id}/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    balance = account_service.get_balance(db, account_id)
    account = account_service.get_account(db, account_id)
    return {"account_id": account_id, "balance_minor": balance, "commodity_id": account.commodity_id}


@router.get("/{account_id}/register")
def get_register(
    account_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    from ..models.transaction import Transaction
    from ..models.account import Account

    account_service.get_account(db, account_id)  # 404 check

    splits_with_balance = account_service.get_register(db, account_id, limit, offset)

    result = []
    for entry in splits_with_balance:
        split = entry["split"]
        txn = split.transaction
        # Find transfer account (the other side)
        other_splits = [s for s in txn.splits if s.account_id != account_id]
        transfer_names = []
        for os in other_splits:
            other_acct = db.get(Account, os.account_id)
            if other_acct:
                transfer_names.append(other_acct.full_name)

        result.append({
            "split_id": split.id,
            "transaction_id": txn.id,
            "date": txn.date,
            "description": txn.description,
            "memo": split.memo,
            "transfer": ", ".join(transfer_names),
            "quantity_minor": split.quantity_minor,
            "reconciled": split.reconciled,
            "running_balance": entry["running_balance"],
        })

    return result
