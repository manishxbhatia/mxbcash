import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import type { PnLReport as PnLData } from "../../types";
import { formatCents } from "../../utils/money";

interface Props {
  report: PnLData;
  fraction: number;
}

export default function PnLReport({ report, fraction }: Props) {
  // Aggregate by period: sum income and expense separately
  const periodMap: Record<string, { period: string; income: number; expense: number }> = {};

  for (const row of report.rows) {
    if (!periodMap[row.period]) {
      periodMap[row.period] = { period: row.period, income: 0, expense: 0 };
    }
    if (row.account_type === "INCOME") {
      // Income is negative in double-entry; negate for display
      periodMap[row.period].income += -row.amount_minor;
    } else {
      periodMap[row.period].expense += row.amount_minor;
    }
  }

  const data = Object.values(periodMap).sort((a, b) => a.period.localeCompare(b.period));

  const fmt = (v: number) => formatCents(v, fraction);

  if (data.length === 0) {
    return <p style={{ color: "var(--muted)", marginTop: "1rem" }}>No data for selected period.</p>;
  }

  return (
    <div>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => fmt(v)} />
            <Legend />
            <Bar dataKey="income" name="Income" fill="#22c55e" />
            <Bar dataKey="expense" name="Expenses" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <table style={{ marginTop: "1.5rem" }}>
        <thead>
          <tr>
            <th>Account</th>
            <th>Type</th>
            <th>Period</th>
            <th style={{ textAlign: "right" }}>Amount ({report.reporting_currency})</th>
          </tr>
        </thead>
        <tbody>
          {report.rows.map((row, i) => (
            <tr key={i}>
              <td>{row.account_name}</td>
              <td>{row.account_type}</td>
              <td>{row.period}</td>
              <td style={{ textAlign: "right" }}>
                <span className={row.amount_minor >= 0 ? "" : "positive"}>
                  {formatCents(row.amount_minor, fraction)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
