import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { BalanceHistory } from "../../types";
import { formatCents } from "../../utils/money";

interface Props {
  history: BalanceHistory;
  fraction: number;
}

export default function BalanceChart({ history, fraction }: Props) {
  const data = history.points.map((p) => ({
    period: p.period,
    balance: p.balance_minor,
  }));

  const fmt = (v: number) => formatCents(v, fraction);

  if (data.length === 0) {
    return <p style={{ color: "var(--muted)", marginTop: "1rem" }}>No data for selected period.</p>;
  }

  return (
    <div>
      <h3 style={{ marginBottom: "0.5rem" }}>{history.account_name}</h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => fmt(v)} />
            <Line type="monotone" dataKey="balance" name="Balance" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
