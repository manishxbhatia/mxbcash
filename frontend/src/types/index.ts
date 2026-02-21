export type AccountType = "ASSET" | "LIABILITY" | "EQUITY" | "INCOME" | "EXPENSE";

export interface Commodity {
  id: number;
  mnemonic: string;
  name: string;
  fraction: number;
}

export interface Price {
  id: number;
  date: string;
  commodity_id: number;
  currency_id: number;
  numerator: number;
  denominator: number;
  source: string;
}

export interface Account {
  id: number;
  name: string;
  full_name: string;
  account_type: AccountType;
  description: string | null;
  placeholder: boolean;
  commodity_id: number;
  parent_id: number | null;
}

export interface AccountTreeNode extends Account {
  children: AccountTreeNode[];
}

export interface Split {
  id: number;
  transaction_id: number;
  account_id: number;
  value_minor: number;
  quantity_minor: number;
  memo: string | null;
  reconciled: string;
}

export interface Transaction {
  id: number;
  date: string;
  description: string;
  notes: string | null;
  import_ref: string | null;
  currency_id: number;
  splits: Split[];
}

export interface RegisterEntry {
  split_id: number;
  transaction_id: number;
  date: string;
  description: string;
  memo: string | null;
  transfer: string;
  quantity_minor: number;
  reconciled: string;
  running_balance: number;
}

export interface PnLRow {
  account_id: number;
  account_name: string;
  account_type: string;
  period: string;
  amount_minor: number;
  reporting_currency: string;
}

export interface PnLReport {
  rows: PnLRow[];
  reporting_currency: string;
  from_date: string;
  to_date: string;
}

export interface BalancePoint {
  period: string;
  balance_minor: number;
  reporting_currency: string;
}

export interface BalanceHistory {
  account_id: number;
  account_name: string;
  points: BalancePoint[];
  reporting_currency: string;
}

export interface NetWorthSnapshot {
  assets_minor: number;
  liabilities_minor: number;
  net_worth_minor: number;
  reporting_currency: string;
}
