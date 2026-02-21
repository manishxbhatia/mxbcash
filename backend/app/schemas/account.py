from typing import Optional, List
from pydantic import BaseModel
from ..models.account import AccountType


class AccountCreate(BaseModel):
    name: str
    account_type: AccountType
    commodity_id: int
    parent_id: Optional[int] = None
    description: str = ""
    placeholder: bool = False


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    placeholder: Optional[bool] = None
    parent_id: Optional[int] = None


class AccountRead(BaseModel):
    id: int
    name: str
    full_name: str
    account_type: AccountType
    description: Optional[str] = None
    placeholder: bool
    commodity_id: int
    parent_id: Optional[int] = None

    model_config = {"from_attributes": True}


class AccountTreeNode(AccountRead):
    children: List["AccountTreeNode"] = []

    model_config = {"from_attributes": True}


AccountTreeNode.model_rebuild()
