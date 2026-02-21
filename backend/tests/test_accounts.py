"""Tests for account CRUD and tree structure."""
import pytest
from fastapi.testclient import TestClient


def test_list_accounts(client: TestClient):
    resp = client.get("/api/v1/accounts")
    assert resp.status_code == 200
    accounts = resp.json()
    assert len(accounts) > 0
    # Seed should have created Assets, Liabilities, etc.
    full_names = [a["full_name"] for a in accounts]
    assert any("Assets" in fn for fn in full_names)
    assert any("Expenses" in fn for fn in full_names)


def test_account_tree(client: TestClient):
    resp = client.get("/api/v1/accounts?tree=true")
    assert resp.status_code == 200
    tree = resp.json()
    # Root nodes have no parent
    root_names = [n["name"] for n in tree]
    assert "Assets" in root_names or any(n["name"] == "Assets" for n in tree)


def test_create_account(client: TestClient):
    # Get USD commodity id
    commodities = client.get("/api/v1/commodities").json()
    usd = next(c for c in commodities if c["mnemonic"] == "USD")

    resp = client.post("/api/v1/accounts", json={
        "name": "Test Checking",
        "account_type": "ASSET",
        "commodity_id": usd["id"],
        "parent_id": None,
        "description": "Test account",
        "placeholder": False,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Checking"
    assert data["full_name"] == "Test Checking"
    assert data["account_type"] == "ASSET"


def test_get_account(client: TestClient):
    accounts = client.get("/api/v1/accounts").json()
    acct = accounts[0]
    resp = client.get(f"/api/v1/accounts/{acct['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == acct["id"]


def test_get_account_not_found(client: TestClient):
    resp = client.get("/api/v1/accounts/99999")
    assert resp.status_code == 404


def test_account_balance(client: TestClient):
    accounts = client.get("/api/v1/accounts").json()
    acct = next(a for a in accounts if not a["placeholder"])
    resp = client.get(f"/api/v1/accounts/{acct['id']}/balance")
    assert resp.status_code == 200
    assert "balance_minor" in resp.json()


def test_full_name_with_parent(client: TestClient):
    """Child account full_name should be 'Parent:Child'."""
    commodities = client.get("/api/v1/commodities").json()
    usd = next(c for c in commodities if c["mnemonic"] == "USD")

    parent_resp = client.post("/api/v1/accounts", json={
        "name": "TestParent",
        "account_type": "EXPENSE",
        "commodity_id": usd["id"],
        "placeholder": True,
    })
    parent = parent_resp.json()

    child_resp = client.post("/api/v1/accounts", json={
        "name": "TestChild",
        "account_type": "EXPENSE",
        "commodity_id": usd["id"],
        "parent_id": parent["id"],
    })
    child = child_resp.json()
    assert child["full_name"] == "TestParent:TestChild"
