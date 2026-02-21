# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mxbcash** — A local-first GnuCash-like personal finance web app.

- **Backend:** Python + FastAPI + SQLAlchemy + SQLite + Alembic
- **Frontend:** React + TypeScript + Vite + Zustand + Recharts

## Project Layout

```
mxbcash/
├── Makefile                        # make dev / make build / make start / make test
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini + alembic/versions/
│   └── app/
│       ├── main.py                 # FastAPI app; serves static build in prod
│       ├── config.py               # Settings (DB path via MXBCASH_DB_PATH)
│       ├── database.py             # Engine, SessionLocal, Base, get_db()
│       ├── seed.py                 # First-run seed: currencies + chart of accounts
│       ├── models/                 # SQLAlchemy models (Commodity, Price, Account, Transaction, Split)
│       ├── schemas/                # Pydantic request/response models
│       ├── routers/                # accounts, transactions, commodities/prices, reports
│       └── services/               # account_service, transaction_service, report_service
└── frontend/
    ├── vite.config.ts              # proxies /api → localhost:8000 in dev
    └── src/
        ├── api/                    # typed API client functions
        ├── types/index.ts          # TypeScript interfaces
        ├── store/                  # Zustand stores (accountStore, transactionStore)
        ├── pages/                  # AccountsPage, RegisterPage, TransactionPage, ReportsPage
        ├── components/             # accounts/, transactions/, reports/
        └── utils/                  # money.ts (parseCents/formatCents), dates.ts
```

## Key Architecture Notes

- **Double-entry accounting:** All transactions require `sum(split.value_minor) == 0` — enforced in `transaction_service.py`.
- **Integer amounts:** All money stored/transported as integer minor units (e.g. cents for USD). Never floats.
- **API prefix:** All backend endpoints are at `/api/v1/` (e.g. `/api/v1/accounts`).
- **Seed data:** On first run (empty `accounts` table), currencies and a standard chart of accounts are auto-seeded.
- **Production serving:** `make build` copies `frontend/dist/` → `backend/app/static/`; FastAPI serves the SPA.

## Commands

```bash
# First-time setup
make install

# Run database migrations (after install)
make migrate

# Development (backend :8000 + frontend :5173)
make dev

# Run tests
make test

# Production build + serve
make build && make start
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MXBCASH_DB_PATH` | `backend/mxbcash.db` | Path to SQLite database file |
| `MXBCASH_DEBUG` | `false` | Enable SQLAlchemy query logging |
| `MXBCASH_DEFAULT_REPORTING_CURRENCY` | `USD` | Default currency for reports |

## API Endpoints (`/api/v1`)

- `GET /commodities` — list currencies
- `GET/POST /prices`, `GET /prices/latest?from=EUR&to=USD`
- `GET/POST /accounts?tree=true`, `GET/PATCH/DELETE /accounts/{id}`
- `GET /accounts/{id}/balance`, `GET /accounts/{id}/register`
- `GET/POST /transactions`, `GET/PATCH/DELETE /transactions/{id}`
- `GET /reports/pnl?from_date&to_date&group_by&reporting_currency`
- `GET /reports/balance-history?account_id&from_date&to_date&group_by&reporting_currency`
- `GET /reports/net-worth?reporting_currency`

## Testing

```bash
make test
# or directly:
backend/.venv/bin/pytest backend/tests/ -v
```

Tests use an in-memory SQLite database. Key test files:
- `backend/tests/test_accounts.py` — account CRUD, tree, full_name
- `backend/tests/test_transactions.py` — zero-sum enforcement, register running balance
- `backend/tests/test_reports.py` — P&L, balance history, net worth
