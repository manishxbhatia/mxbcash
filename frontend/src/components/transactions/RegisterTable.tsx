import { useNavigate } from "react-router-dom";
import type { RegisterEntry, Commodity } from "../../types";
import { formatCents } from "../../utils/money";
import { formatDate } from "../../utils/dates";

interface Props {
  entries: RegisterEntry[];
  commodity: Commodity;
  onDelete?: (txnId: number) => void;
}

export default function RegisterTable({ entries, commodity, onDelete }: Props) {
  const navigate = useNavigate();

  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Description</th>
          <th>Transfer</th>
          <th>Deposit</th>
          <th>Withdrawal</th>
          <th>Balance</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {entries.length === 0 && (
          <tr>
            <td colSpan={7} style={{ color: "var(--muted)", textAlign: "center", padding: "2rem" }}>
              No transactions yet.
            </td>
          </tr>
        )}
        {entries.map((e) => {
          const isDeposit = e.quantity_minor >= 0;
          return (
            <tr key={e.split_id}>
              <td>{formatDate(e.date)}</td>
              <td>
                <span
                  style={{ cursor: "pointer", color: "var(--accent)" }}
                  onClick={() => navigate(`/transactions/${e.transaction_id}/edit`)}
                >
                  {e.description || "(no description)"}
                </span>
                {e.memo && <span style={{ color: "var(--muted)", marginLeft: "0.4rem", fontSize: "11px" }}>{e.memo}</span>}
              </td>
              <td style={{ color: "var(--muted)" }}>{e.transfer}</td>
              <td className="positive">
                {isDeposit ? formatCents(e.quantity_minor, commodity.fraction) : ""}
              </td>
              <td className="negative">
                {!isDeposit ? formatCents(Math.abs(e.quantity_minor), commodity.fraction) : ""}
              </td>
              <td style={{ fontWeight: 500 }}>
                <span className={e.running_balance >= 0 ? "positive" : "negative"}>
                  {formatCents(e.running_balance, commodity.fraction)}
                </span>
              </td>
              <td>
                {onDelete && (
                  <button
                    className="btn btn-danger"
                    style={{ padding: "0.15rem 0.4rem", fontSize: "11px" }}
                    onClick={() => {
                      if (confirm("Delete this transaction?")) onDelete(e.transaction_id);
                    }}
                  >Del</button>
                )}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
