import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAccountStore } from "../store/accountStore";
import PnLReportComp from "../components/reports/PnLReport";
import BalanceChartComp from "../components/reports/BalanceChart";
import * as api from "../api";
import type { PnLReport, BalanceHistory } from "../types";
import { today, monthsAgo } from "../utils/dates";

interface Props {
  tab: "pnl" | "balance";
}

export default function ReportsPage({ tab }: Props) {
  const navigate = useNavigate();
  const { accounts, commodities, fetchAccounts, fetchCommodities } = useAccountStore();

  const [fromDate, setFromDate] = useState(monthsAgo(12));
  const [toDate, setToDate] = useState(today());
  const [groupBy, setGroupBy] = useState("month");
  const [reportingCurrency, setReportingCurrency] = useState("USD");
  const [selectedAccountId, setSelectedAccountId] = useState<number>(0);

  const [pnlReport, setPnlReport] = useState<PnLReport | null>(null);
  const [balanceHistory, setBalanceHistory] = useState<BalanceHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAccounts();
    fetchCommodities();
  }, []);

  useEffect(() => {
    if (accounts.length > 0 && selectedAccountId === 0) {
      const first = accounts.find((a) => !a.placeholder);
      if (first) setSelectedAccountId(first.id);
    }
  }, [accounts]);

  const fraction = commodities.find((c) => c.mnemonic === reportingCurrency)?.fraction ?? 100;

  async function run() {
    setLoading(true);
    setError(null);
    try {
      if (tab === "pnl") {
        const report = await api.getPnL({ from_date: fromDate, to_date: toDate, group_by: groupBy, reporting_currency: reportingCurrency });
        setPnlReport(report);
      } else {
        if (!selectedAccountId) return;
        const hist = await api.getBalanceHistory({
          account_id: selectedAccountId,
          from_date: fromDate,
          to_date: toDate,
          group_by: groupBy,
          reporting_currency: reportingCurrency,
        });
        setBalanceHistory(hist);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{tab === "pnl" ? "P&L Report" : "Balance History"}</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            className={`btn ${tab === "pnl" ? "btn-primary" : "btn-ghost"}`}
            onClick={() => navigate("/reports/pnl")}
          >P&L</button>
          <button
            className={`btn ${tab === "balance" ? "btn-primary" : "btn-ghost"}`}
            onClick={() => navigate("/reports/balance")}
          >Balance History</button>
        </div>
      </div>

      <div className="card">
        <div className="filter-row">
          <div>
            <label>From</label>
            <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
          </div>
          <div>
            <label>To</label>
            <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
          </div>
          <div>
            <label>Group by</label>
            <select value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
              <option value="day">Day</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
            </select>
          </div>
          <div>
            <label>Reporting currency</label>
            <select value={reportingCurrency} onChange={(e) => setReportingCurrency(e.target.value)}>
              {commodities.map((c) => <option key={c.id} value={c.mnemonic}>{c.mnemonic}</option>)}
            </select>
          </div>
          {tab === "balance" && (
            <div>
              <label>Account</label>
              <select value={selectedAccountId} onChange={(e) => setSelectedAccountId(Number(e.target.value))}>
                {accounts.filter((a) => !a.placeholder).map((a) => (
                  <option key={a.id} value={a.id}>{a.full_name}</option>
                ))}
              </select>
            </div>
          )}
          <div style={{ alignSelf: "flex-end" }}>
            <button className="btn btn-primary" onClick={run} disabled={loading}>
              {loading ? "Loading…" : "Run Report"}
            </button>
          </div>
        </div>

        {error && <div className="alert-error">{error}</div>}

        {tab === "pnl" && pnlReport && (
          <PnLReportComp report={pnlReport} fraction={fraction} />
        )}
        {tab === "balance" && balanceHistory && (
          <BalanceChartComp history={balanceHistory} fraction={fraction} />
        )}
        {!loading && !pnlReport && !balanceHistory && (
          <p style={{ color: "var(--muted)", textAlign: "center", padding: "2rem" }}>
            Select filters above and click "Run Report"
          </p>
        )}
      </div>
    </div>
  );
}
