import { useEffect, useState } from "react";
import { useAccountStore } from "../store/accountStore";
import type { AccountTreeNode as TreeNode } from "../types";
import AccountTreeNodeComp from "../components/accounts/AccountTreeNode";
import AccountForm from "../components/accounts/AccountForm";
import * as api from "../api";

export default function AccountsPage() {
  const { tree, accounts, commodities, loading, error, fetchTree, fetchAccounts, fetchCommodities, createAccount, updateAccount, deleteAccount } =
    useAccountStore();

  const [balances, setBalances] = useState<Record<number, number>>({});
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<TreeNode | null>(null);
  const [netWorth, setNetWorth] = useState<{ assets_minor: number; liabilities_minor: number; net_worth_minor: number } | null>(null);

  useEffect(() => {
    fetchTree();
    fetchAccounts();
    fetchCommodities();
    api.getNetWorth().then(setNetWorth).catch(() => {});
  }, []);

  // Fetch balances for all non-placeholder accounts
  useEffect(() => {
    const nonPlaceholders = accounts.filter((a) => !a.placeholder);
    Promise.all(
      nonPlaceholders.map((a) =>
        api.getAccountBalance(a.id).then((r) => ({ id: a.id, bal: r.balance_minor }))
      )
    ).then((results) => {
      const map: Record<number, number> = {};
      for (const r of results) map[r.id] = r.bal;
      setBalances(map);
    });
  }, [accounts]);

  async function handleCreate(data: Parameters<typeof createAccount>[0]) {
    await createAccount(data);
    await fetchTree();
    await fetchAccounts();
    setShowForm(false);
  }

  async function handleEdit(data: Parameters<typeof updateAccount>[1]) {
    if (!editing) return;
    await updateAccount(editing.id, data);
    await fetchTree();
    await fetchAccounts();
    setEditing(null);
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this account? This cannot be undone.")) return;
    try {
      await deleteAccount(id);
      await fetchTree();
      await fetchAccounts();
    } catch (e) {
      alert(String(e));
    }
  }

  const usd = commodities.find((c) => c.mnemonic === "USD");

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Accounts</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ New Account</button>
      </div>

      {netWorth && usd && (
        <div className="card" style={{ display: "flex", gap: "2rem", marginBottom: "1rem" }}>
          <div>
            <div style={{ color: "var(--muted)", fontSize: "12px" }}>Assets</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--success)" }}>
              {usd.mnemonic} {(netWorth.assets_minor / usd.fraction).toFixed(2)}
            </div>
          </div>
          <div>
            <div style={{ color: "var(--muted)", fontSize: "12px" }}>Liabilities</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--danger)" }}>
              {usd.mnemonic} {(Math.abs(netWorth.liabilities_minor) / usd.fraction).toFixed(2)}
            </div>
          </div>
          <div>
            <div style={{ color: "var(--muted)", fontSize: "12px" }}>Net Worth</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 600 }}>
              {usd.mnemonic} {(netWorth.net_worth_minor / usd.fraction).toFixed(2)}
            </div>
          </div>
        </div>
      )}

      {error && <div className="alert-error">{error}</div>}

      <div className="card">
        {loading ? (
          <p style={{ color: "var(--muted)" }}>Loading…</p>
        ) : (
          tree.map((node) => (
            <AccountTreeNodeComp
              key={node.id}
              node={node}
              commodities={commodities}
              balances={balances}
              onEdit={setEditing}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {(showForm || editing) && (
        <div className="modal-overlay" onClick={() => { setShowForm(false); setEditing(null); }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span>{editing ? "Edit Account" : "New Account"}</span>
              <button className="btn btn-ghost" onClick={() => { setShowForm(false); setEditing(null); }}>✕</button>
            </div>
            <AccountForm
              accounts={accounts}
              commodities={commodities}
              initial={editing ?? undefined}
              onSubmit={editing ? handleEdit : handleCreate}
              onCancel={() => { setShowForm(false); setEditing(null); }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
