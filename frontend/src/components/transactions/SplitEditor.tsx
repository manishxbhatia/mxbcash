import type { Account, Commodity } from "../../types";
import { formatCents, parseCents } from "../../utils/money";

export interface SplitDraft {
  account_id: number;
  value_str: string;  // display string in transaction currency
  quantity_str: string;  // display string in account currency (for FX)
  memo: string;
  reconciled: string;
}

export function draftToSplit(d: SplitDraft, fraction: number) {
  const value_minor = parseCents(d.value_str || "0", fraction);
  const qty_str = d.quantity_str.trim() || d.value_str;
  const acct_fraction = fraction; // simplified: use tx fraction unless overridden
  const quantity_minor = parseCents(qty_str || "0", acct_fraction);
  return {
    account_id: d.account_id,
    value_minor,
    quantity_minor,
    memo: d.memo,
    reconciled: d.reconciled,
  };
}

interface Props {
  splits: SplitDraft[];
  accounts: Account[];
  commodities: Commodity[];
  txCurrencyFraction: number;
  onChange: (splits: SplitDraft[]) => void;
}

export default function SplitEditor({ splits, accounts, commodities, txCurrencyFraction, onChange }: Props) {
  function update(index: number, field: keyof SplitDraft, value: string | number) {
    const next = splits.map((s, i) => (i === index ? { ...s, [field]: value } : s));
    onChange(next);
  }

  function addSplit() {
    onChange([...splits, { account_id: accounts[0]?.id ?? 0, value_str: "", quantity_str: "", memo: "", reconciled: "n" }]);
  }

  function removeSplit(index: number) {
    onChange(splits.filter((_, i) => i !== index));
  }

  // Compute imbalance
  const total = splits.reduce((sum, s) => {
    const v = parseCents(s.value_str || "0", txCurrencyFraction);
    return sum + v;
  }, 0);
  const balanced = total === 0;

  function getCommodity(accountId: number) {
    const acct = accounts.find((a) => a.id === accountId);
    return commodities.find((c) => c.id === acct?.commodity_id);
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
        <strong>Splits</strong>
        <span className={balanced ? "badge-balanced" : "badge-imbalanced"}>
          {balanced ? "✓ Balanced" : `Imbalance: ${formatCents(total, txCurrencyFraction)}`}
        </span>
      </div>

      <div style={{ fontWeight: 600, fontSize: "12px", color: "var(--muted)", display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr auto", gap: "0.5rem", padding: "0.2rem 0" }}>
        <span>Account</span>
        <span>Value (tx currency)</span>
        <span>Quantity (acct currency)</span>
        <span>Memo</span>
        <span></span>
      </div>

      {splits.map((split, i) => {
        const acctCommodity = getCommodity(split.account_id);
        const sameAsBase = !acctCommodity || acctCommodity.fraction === txCurrencyFraction;
        return (
          <div key={i} className="split-row">
            <select
              value={split.account_id}
              onChange={(e) => update(i, "account_id", Number(e.target.value))}
            >
              {accounts.map((a) => (
                <option key={a.id} value={a.id} disabled={a.placeholder}>
                  {a.full_name}
                </option>
              ))}
            </select>
            <input
              type="text"
              placeholder="0.00"
              value={split.value_str}
              onChange={(e) => update(i, "value_str", e.target.value)}
            />
            <input
              type="text"
              placeholder={sameAsBase ? "same" : "0.00"}
              value={split.quantity_str}
              onChange={(e) => update(i, "quantity_str", e.target.value)}
              disabled={sameAsBase}
              style={{ opacity: sameAsBase ? 0.4 : 1 }}
            />
            <input
              type="text"
              placeholder="Memo"
              value={split.memo}
              onChange={(e) => update(i, "memo", e.target.value)}
            />
            <button
              type="button"
              className="btn btn-danger"
              style={{ padding: "0.2rem 0.5rem" }}
              onClick={() => removeSplit(i)}
              disabled={splits.length <= 2}
            >✕</button>
          </div>
        );
      })}

      <button type="button" className="btn btn-ghost" style={{ marginTop: "0.5rem" }} onClick={addSplit}>
        + Add Split
      </button>
    </div>
  );
}
