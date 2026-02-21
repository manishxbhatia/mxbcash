import { useState } from "react";
import type { Account, AccountTreeNode, Commodity } from "../../types";

interface Props {
  accounts: Account[];
  commodities: Commodity[];
  initial?: Partial<Account>;
  onSubmit: (data: Omit<Account, "id" | "full_name">) => Promise<void>;
  onCancel: () => void;
}

const TYPES = ["ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"] as const;

export default function AccountForm({ accounts, commodities, initial, onSubmit, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [account_type, setType] = useState<Account["account_type"]>(initial?.account_type ?? "EXPENSE");
  const [commodity_id, setCommodity] = useState(initial?.commodity_id ?? commodities[0]?.id ?? 0);
  const [parent_id, setParent] = useState<number | null>(initial?.parent_id ?? null);
  const [description, setDescription] = useState(initial?.description ?? "");
  const [placeholder, setPlaceholder] = useState(initial?.placeholder ?? false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ name, account_type, commodity_id, parent_id, description, placeholder });
    } catch (err) {
      setError(String(err));
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="alert-error">{error}</div>}
      <div className="form-group">
        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div className="form-group">
        <label>Type</label>
        <select value={account_type} onChange={(e) => setType(e.target.value as Account["account_type"])}>
          {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label>Currency</label>
        <select value={commodity_id} onChange={(e) => setCommodity(Number(e.target.value))}>
          {commodities.map((c) => (
            <option key={c.id} value={c.id}>{c.mnemonic} – {c.name}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Parent Account</label>
        <select value={parent_id ?? ""} onChange={(e) => setParent(e.target.value ? Number(e.target.value) : null)}>
          <option value="">(none — root)</option>
          {accounts.map((a) => (
            <option key={a.id} value={a.id}>{a.full_name}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Description</label>
        <input value={description} onChange={(e) => setDescription(e.target.value)} />
      </div>
      <div className="form-group" style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <input
          type="checkbox"
          id="placeholder"
          checked={placeholder}
          onChange={(e) => setPlaceholder(e.target.checked)}
          style={{ width: "auto" }}
        />
        <label htmlFor="placeholder" style={{ margin: 0 }}>Placeholder (no transactions)</label>
      </div>
      <div className="modal-footer">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : "Save"}
        </button>
      </div>
    </form>
  );
}
