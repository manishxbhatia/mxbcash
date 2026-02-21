import { get, post, patch, del } from "./client";
import type {
  Account,
  AccountTreeNode,
  Commodity,
  Price,
  Transaction,
  RegisterEntry,
  PnLReport,
  BalanceHistory,
  NetWorthSnapshot,
} from "../types";

// Commodities
export const getCommodities = () => get<Commodity[]>("/commodities");
export const getPrices = () => get<Price[]>("/prices");
export const createPrice = (data: Omit<Price, "id">) => post<Price>("/prices", data);
export const getLatestPrice = (from: string, to: string) =>
  get<Price | null>(`/prices/latest?from=${from}&to=${to}`);

// Accounts
export const getAccounts = () => get<Account[]>("/accounts");
export const getAccountTree = () => get<AccountTreeNode[]>("/accounts?tree=true");
export const createAccount = (data: Omit<Account, "id" | "full_name">) =>
  post<Account>("/accounts", data);
export const updateAccount = (
  id: number,
  data: Partial<Pick<Account, "name" | "description" | "placeholder" | "parent_id">>
) => patch<Account>(`/accounts/${id}`, data);
export const deleteAccount = (id: number) => del(`/accounts/${id}`);
export const getAccountBalance = (id: number) =>
  get<{ account_id: number; balance_minor: number; commodity_id: number }>(`/accounts/${id}/balance`);
export const getRegister = (id: number, limit = 100, offset = 0) =>
  get<RegisterEntry[]>(`/accounts/${id}/register?limit=${limit}&offset=${offset}`);

// Transactions
export const getTransactions = (params?: {
  account_id?: number;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}) => {
  const qs = new URLSearchParams();
  if (params?.account_id) qs.set("account_id", String(params.account_id));
  if (params?.from_date) qs.set("from_date", params.from_date);
  if (params?.to_date) qs.set("to_date", params.to_date);
  if (params?.limit) qs.set("limit", String(params.limit));
  if (params?.offset) qs.set("offset", String(params.offset));
  const q = qs.toString();
  return get<Transaction[]>(`/transactions${q ? `?${q}` : ""}`);
};
export const getTransaction = (id: number) => get<Transaction>(`/transactions/${id}`);
export const createTransaction = (data: Omit<Transaction, "id" | "splits"> & { splits: Array<Omit<Transaction["splits"][0], "id" | "transaction_id">> }) =>
  post<Transaction>("/transactions", data);
export const updateTransaction = (id: number, data: Partial<Omit<Transaction, "id">>) =>
  patch<Transaction>(`/transactions/${id}`, data);
export const deleteTransaction = (id: number) => del(`/transactions/${id}`);

// Reports
export const getPnL = (params: {
  from_date: string;
  to_date: string;
  group_by?: string;
  reporting_currency?: string;
}) => {
  const qs = new URLSearchParams(params as Record<string, string>);
  return get<PnLReport>(`/reports/pnl?${qs}`);
};

export const getBalanceHistory = (params: {
  account_id: number;
  from_date: string;
  to_date: string;
  group_by?: string;
  reporting_currency?: string;
}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]))
  );
  return get<BalanceHistory>(`/reports/balance-history?${qs}`);
};

export const getNetWorth = (reportingCurrency = "USD") =>
  get<NetWorthSnapshot>(`/reports/net-worth?reporting_currency=${reportingCurrency}`);
