import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import AccountsPage from "./pages/AccountsPage";
import RegisterPage from "./pages/RegisterPage";
import TransactionPage from "./pages/TransactionPage";
import ReportsPage from "./pages/ReportsPage";

export default function App() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">mxbcash</div>
        <nav className="sidebar-nav">
          <NavLink to="/accounts">Accounts</NavLink>
          <NavLink to="/transactions/new">New Transaction</NavLink>
          <NavLink to="/reports/pnl">P&amp;L Report</NavLink>
          <NavLink to="/reports/balance">Balance History</NavLink>
        </nav>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/accounts" replace />} />
          <Route path="/accounts" element={<AccountsPage />} />
          <Route path="/accounts/:id/register" element={<RegisterPage />} />
          <Route path="/transactions/new" element={<TransactionPage />} />
          <Route path="/transactions/:id/edit" element={<TransactionPage />} />
          <Route path="/reports/pnl" element={<ReportsPage tab="pnl" />} />
          <Route path="/reports/balance" element={<ReportsPage tab="balance" />} />
        </Routes>
      </main>
    </div>
  );
}
