"""Tests for P&L and balance history reports."""
import pytest
from fastapi.testclient import TestClient


def _setup_transactions(client):
    """Create test transactions for report testing."""
    commodities = client.get("/api/v1/commodities").json()
    usd = next(c for c in commodities if c["mnemonic"] == "USD")

    accounts = client.get("/api/v1/accounts").json()
    income = next(a for a in accounts if a["account_type"] == "INCOME" and not a["placeholder"])
    expense = next(a for a in accounts if a["account_type"] == "EXPENSE" and not a["placeholder"])

    checking = client.post("/api/v1/accounts", json={
        "name": "ReportTestChecking",
        "account_type": "ASSET",
        "commodity_id": usd["id"],
    }).json()

    # Jan: salary 3000, groceries 200
    client.post("/api/v1/transactions", json={
        "date": "2024-01-15",
        "description": "Salary Jan",
        "currency_id": usd["id"],
        "splits": [
            {"account_id": checking["id"], "value_minor": 300000, "quantity_minor": 300000},
            {"account_id": income["id"], "value_minor": -300000, "quantity_minor": -300000},
        ],
    })
    client.post("/api/v1/transactions", json={
        "date": "2024-01-20",
        "description": "Groceries Jan",
        "currency_id": usd["id"],
        "splits": [
            {"account_id": expense["id"], "value_minor": 20000, "quantity_minor": 20000},
            {"account_id": checking["id"], "value_minor": -20000, "quantity_minor": -20000},
        ],
    })
    return checking, income, expense, usd


def test_pnl_report(client: TestClient):
    checking, income, expense, usd = _setup_transactions(client)

    resp = client.get(
        "/api/v1/reports/pnl",
        params={"from_date": "2024-01-01", "to_date": "2024-01-31", "group_by": "month", "reporting_currency": "USD"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "rows" in data
    assert data["reporting_currency"] == "USD"


def test_balance_history(client: TestClient):
    checking, income, expense, usd = _setup_transactions(client)

    resp = client.get(
        "/api/v1/reports/balance-history",
        params={
            "account_id": checking["id"],
            "from_date": "2024-01-01",
            "to_date": "2024-12-31",
            "group_by": "month",
            "reporting_currency": "USD",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "points" in data
    assert data["account_id"] == checking["id"]
    assert len(data["points"]) > 0


def test_net_worth(client: TestClient):
    resp = client.get("/api/v1/reports/net-worth", params={"reporting_currency": "USD"})
    assert resp.status_code == 200
    data = resp.json()
    assert "net_worth_minor" in data
    assert data["reporting_currency"] == "USD"
