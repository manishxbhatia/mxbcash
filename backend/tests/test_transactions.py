"""Tests for transaction creation, zero-sum enforcement, and register."""
import pytest
from fastapi.testclient import TestClient


def _get_two_accounts(client):
    """Return two non-placeholder accounts for testing."""
    accounts = client.get("/api/v1/accounts").json()
    non_placeholder = [a for a in accounts if not a["placeholder"]]
    return non_placeholder[0], non_placeholder[1]


def _get_usd_id(client):
    commodities = client.get("/api/v1/commodities").json()
    return next(c for c in commodities if c["mnemonic"] == "USD")["id"]


def test_create_transaction_balanced(client: TestClient):
    acct1, acct2 = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    resp = client.post("/api/v1/transactions", json={
        "date": "2024-03-15",
        "description": "Test transaction",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 5000, "quantity_minor": 5000, "memo": "", "reconciled": "n"},
            {"account_id": acct2["id"], "value_minor": -5000, "quantity_minor": -5000, "memo": "", "reconciled": "n"},
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Test transaction"
    assert len(data["splits"]) == 2


def test_create_transaction_imbalanced(client: TestClient):
    """Transaction with non-zero splits must be rejected."""
    acct1, acct2 = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    resp = client.post("/api/v1/transactions", json={
        "date": "2024-03-15",
        "description": "Bad transaction",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 5000, "quantity_minor": 5000},
            {"account_id": acct2["id"], "value_minor": -4999, "quantity_minor": -4999},
        ],
    })
    assert resp.status_code == 422


def test_create_transaction_single_split(client: TestClient):
    """Transaction with only one split must be rejected."""
    acct1, _ = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    resp = client.post("/api/v1/transactions", json={
        "date": "2024-03-15",
        "description": "Single split",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 0, "quantity_minor": 0},
        ],
    })
    assert resp.status_code == 422


def test_get_transaction(client: TestClient):
    acct1, acct2 = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    create_resp = client.post("/api/v1/transactions", json={
        "date": "2024-04-01",
        "description": "Payroll",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 300000, "quantity_minor": 300000},
            {"account_id": acct2["id"], "value_minor": -300000, "quantity_minor": -300000},
        ],
    })
    txn_id = create_resp.json()["id"]

    resp = client.get(f"/api/v1/transactions/{txn_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == txn_id


def test_register_running_balance(client: TestClient):
    """Register should have increasing running balances."""
    commodities = client.get("/api/v1/commodities").json()
    usd = next(c for c in commodities if c["mnemonic"] == "USD")

    # Create a fresh checking account
    checking = client.post("/api/v1/accounts", json={
        "name": "BalanceTestChecking",
        "account_type": "ASSET",
        "commodity_id": usd["id"],
    }).json()
    income_accts = client.get("/api/v1/accounts").json()
    income = next(a for a in income_accts if a["account_type"] == "INCOME" and not a["placeholder"])

    # Deposit 100.00
    client.post("/api/v1/transactions", json={
        "date": "2024-01-01",
        "description": "Opening",
        "currency_id": usd["id"],
        "splits": [
            {"account_id": checking["id"], "value_minor": 10000, "quantity_minor": 10000},
            {"account_id": income["id"], "value_minor": -10000, "quantity_minor": -10000},
        ],
    })

    # Deposit another 50.00
    client.post("/api/v1/transactions", json={
        "date": "2024-01-15",
        "description": "Bonus",
        "currency_id": usd["id"],
        "splits": [
            {"account_id": checking["id"], "value_minor": 5000, "quantity_minor": 5000},
            {"account_id": income["id"], "value_minor": -5000, "quantity_minor": -5000},
        ],
    })

    register = client.get(f"/api/v1/accounts/{checking['id']}/register").json()
    assert len(register) == 2
    assert register[0]["running_balance"] == 10000
    assert register[1]["running_balance"] == 15000


def test_update_transaction(client: TestClient):
    acct1, acct2 = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    txn = client.post("/api/v1/transactions", json={
        "date": "2024-05-01",
        "description": "Original",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 1000, "quantity_minor": 1000},
            {"account_id": acct2["id"], "value_minor": -1000, "quantity_minor": -1000},
        ],
    }).json()

    update_resp = client.patch(f"/api/v1/transactions/{txn['id']}", json={
        "description": "Updated",
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated"


def test_delete_transaction(client: TestClient):
    acct1, acct2 = _get_two_accounts(client)
    usd_id = _get_usd_id(client)

    txn = client.post("/api/v1/transactions", json={
        "date": "2024-06-01",
        "description": "To be deleted",
        "currency_id": usd_id,
        "splits": [
            {"account_id": acct1["id"], "value_minor": 500, "quantity_minor": 500},
            {"account_id": acct2["id"], "value_minor": -500, "quantity_minor": -500},
        ],
    }).json()

    del_resp = client.delete(f"/api/v1/transactions/{txn['id']}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/transactions/{txn['id']}")
    assert get_resp.status_code == 404
