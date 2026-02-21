import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAccountStore } from "../store/accountStore";
import { useTransactionStore } from "../store/transactionStore";
import RegisterTable from "../components/transactions/RegisterTable";
import * as api from "../api";
import type { RegisterEntry } from "../types";
import { formatCents } from "../utils/money";

export default function RegisterPage() {
  const { id } = useParams<{ id: string }>();
  const accountId = Number(id);
  const navigate = useNavigate();

  const { accounts, commodities, fetchAccounts, fetchCommodities } = useAccountStore();
  const { deleteTransaction } = useTransactionStore();

  const [entries, setEntries] = useState<RegisterEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    fetchAccounts();
    fetchCommodities();
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getRegister(accountId),
      api.getAccountBalance(accountId),
    ])
      .then(([reg, bal]) => {
        setEntries(reg);
        setBalance(bal.balance_minor);
        setLoading(false);
      })
      .catch((e) => {
        setError(String(e));
        setLoading(false);
      });
  }, [accountId]);

  const account = accounts.find((a) => a.id === accountId);
  const commodity = commodities.find((c) => c.id === account?.commodity_id);

  async function handleDelete(txnId: number) {
    try {
      await deleteTransaction(txnId);
      const [reg, bal] = await Promise.all([
        api.getRegister(accountId),
        api.getAccountBalance(accountId),
      ]);
      setEntries(reg);
      setBalance(bal.balance_minor);
    } catch (e) {
      alert(String(e));
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="btn btn-ghost" onClick={() => navigate("/accounts")} style={{ marginBottom: "0.4rem" }}>
            ← Accounts
          </button>
          <h1 className="page-title">{account?.full_name ?? `Account #${accountId}`}</h1>
          {commodity && (
            <div style={{ color: "var(--muted)", marginTop: "0.2rem" }}>
              Balance: <strong className={balance >= 0 ? "positive" : "negative"}>
                {formatCents(balance, commodity.fraction)} {commodity.mnemonic}
              </strong>
            </div>
          )}
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/transactions/new")}>
          + New Transaction
        </button>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <p style={{ color: "var(--muted)", padding: "2rem" }}>Loading…</p>
        ) : commodity ? (
          <RegisterTable entries={entries} commodity={commodity} onDelete={handleDelete} />
        ) : (
          <p style={{ color: "var(--muted)", padding: "1rem" }}>Account not found.</p>
        )}
      </div>
    </div>
  );
}
