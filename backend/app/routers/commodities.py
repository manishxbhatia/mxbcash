from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.commodity import Commodity, Price
from ..schemas.commodity import CommodityRead, PriceCreate, PriceRead

router = APIRouter(prefix="/commodities", tags=["commodities"])
prices_router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=List[CommodityRead])
def list_commodities(db: Session = Depends(get_db)):
    return db.query(Commodity).order_by(Commodity.mnemonic).all()


@prices_router.get("", response_model=List[PriceRead])
def list_prices(db: Session = Depends(get_db)):
    return db.query(Price).order_by(Price.date.desc()).all()


@prices_router.post("", response_model=PriceRead, status_code=201)
def create_price(data: PriceCreate, db: Session = Depends(get_db)):
    price = Price(**data.model_dump())
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


@prices_router.get("/latest", response_model=Optional[PriceRead])
def latest_price(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    db: Session = Depends(get_db),
):
    from_c = db.query(Commodity).filter(Commodity.mnemonic == from_currency).first()
    to_c = db.query(Commodity).filter(Commodity.mnemonic == to_currency).first()
    if from_c is None or to_c is None:
        return None
    return (
        db.query(Price)
        .filter(Price.commodity_id == from_c.id, Price.currency_id == to_c.id)
        .order_by(Price.date.desc())
        .first()
    )
