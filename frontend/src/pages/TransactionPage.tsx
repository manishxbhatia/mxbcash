import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAccountStore } from "../store/accountStore";
import { useTransactionStore } from "../store/transactionStore";
import SplitEditor, { type SplitDraft, draftToSplit } from "../components/transactions/SplitEditor";
import * as api from "../api";
import { today } from "../utils/dates";
import { parseCents, isBalanced } from "../utils/money";

export default function TransactionPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const { accounts, commodities, fetchAccounts, fetchCommodities } = useAccountStore();
  const { createTransaction, updateTransaction } = useTransactionStore();

  const [date, setDate] = useState(today());
  const [description, setDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [currency_id, setCurrencyId] = useState(0);
  const [splits, setSplits] = useState<SplitDraft[]>([
    { account_id: 0, value_str: "", quantity_str: "", memo: "", reconciled: "n" },
    { account_id: 0, value_str: "", quantity_str: "", memo: "", reconciled: "n" },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAccounts();
    fetchCommodities();
  }, []);

  // Set default currency to USD once commodities load
  useEffect(() => {
    if (currency_id === 0 && commodities.length > 0) {
      const usd = commodities.find((c) => c.mnemonic === "USD");
      setCurrencyId(usd?.id ?? commodities[0].id);
    }
    if (splits[0].account_id === 0 && accounts.length > 0) {
      setSplits((prev) =>
        prev.map((s) => (s.account_id === 0 ? { ...s, account_id: accounts[0].id } : s))
      );
    }
  }, [commodities, accounts]);

  // Load existing transaction for edit
  useEffect(() => {
    if (!isEdit || !id) return;
    api.getTransaction(Number(id)).then((txn) => {
      setDate(String(txn.date));
      setDescription(txn.description);
      setNotes(txn.notes ?? "");
      setCurrencyId(txn.currency_id);
      const frac = commodities.find((c) => c.id === txn.currency_id)?.fraction ?? 100;
      setSplits(
        txn.splits.map((s) => ({
          account_id: s.account_id,
          value_str: (s.value_minor / frac).toFixed(2),
          quantity_str: (s.quantity_minor / frac).toFixed(2),
          memo: s.memo ?? "",
          reconciled: s.reconciled,
        }))
      );
    });
  }, [id, commodities]);

  const txCommodity = commodities.find((c) => c.id === currency_id);
  const fraction = txCommodity?.fraction ?? 100;

  const splitData = splits.map((s) => draftToSplit(s, fraction));
  const balanced = isBalanced(splitData);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!balanced) return;
    setSubmitting(true);
    setError(null);

    try {
      const payload = {
        date,
        description,
        notes,
        currency_id,
        splits: splitData,
      };
      if (isEdit && id) {
        await updateTransaction(Number(id), payload);
      } else {
        await createTransaction(payload);
      }
      navigate(-1);
    } catch (err) {
      setError(String(err));
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ marginBottom: "0.4rem" }}>
            ← Back
          </button>
          <h1 className="page-title">{isEdit ? "Edit Transaction" : "New Transaction"}</h1>
        </div>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Date</label>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Description</label>
              <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Transaction description" />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Currency</label>
              <select value={currency_id} onChange={(e) => setCurrencyId(Number(e.target.value))}>
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>{c.mnemonic}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Notes</label>
            <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" />
          </div>
        </div>

        <div className="card">
          <SplitEditor
            splits={splits}
            accounts={accounts}
            commodities={commodities}
            txCurrencyFraction={fraction}
            onChange={setSplits}
          />
        </div>

        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
          <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>Cancel</button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!balanced || submitting}
            title={!balanced ? "Splits must be balanced before saving" : ""}
          >
            {submitting ? "Saving…" : isEdit ? "Update Transaction" : "Create Transaction"}
          </button>
        </div>
      </form>
    </div>
  );
}
