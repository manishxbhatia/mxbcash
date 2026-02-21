from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.reports import PnLReport, BalanceHistory, NetWorthSnapshot
from ..services import report_service
from ..config import settings

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/pnl", response_model=PnLReport)
def get_pnl(
    from_date: str = Query(...),
    to_date: str = Query(...),
    group_by: str = Query("month", pattern="^(day|month|year)$"),
    reporting_currency: str = Query(settings.default_reporting_currency),
    db: Session = Depends(get_db),
):
    return report_service.get_pnl(db, from_date, to_date, group_by, reporting_currency)


@router.get("/balance-history", response_model=BalanceHistory)
def get_balance_history(
    account_id: int = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...),
    group_by: str = Query("month", pattern="^(day|month|year)$"),
    reporting_currency: str = Query(settings.default_reporting_currency),
    db: Session = Depends(get_db),
):
    return report_service.get_balance_history(
        db, account_id, from_date, to_date, group_by, reporting_currency
    )


@router.get("/net-worth", response_model=NetWorthSnapshot)
def get_net_worth(
    reporting_currency: str = Query(settings.default_reporting_currency),
    db: Session = Depends(get_db),
):
    return report_service.get_net_worth(db, reporting_currency)
