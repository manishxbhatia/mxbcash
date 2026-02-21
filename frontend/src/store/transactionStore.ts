import { create } from "zustand";
import type { Transaction } from "../types";
import * as api from "../api";

interface TransactionState {
  transactions: Transaction[];
  loading: boolean;
  error: string | null;

  fetchTransactions: (params?: Parameters<typeof api.getTransactions>[0]) => Promise<void>;
  createTransaction: (data: Parameters<typeof api.createTransaction>[0]) => Promise<Transaction>;
  updateTransaction: (id: number, data: Parameters<typeof api.updateTransaction>[1]) => Promise<Transaction>;
  deleteTransaction: (id: number) => Promise<void>;
}

export const useTransactionStore = create<TransactionState>((set) => ({
  transactions: [],
  loading: false,
  error: null,

  fetchTransactions: async (params) => {
    set({ loading: true, error: null });
    try {
      const transactions = await api.getTransactions(params);
      set({ transactions, loading: false });
    } catch (e) {
      set({ error: String(e), loading: false });
    }
  },

  createTransaction: async (data) => {
    const txn = await api.createTransaction(data);
    set((s) => ({ transactions: [txn, ...s.transactions] }));
    return txn;
  },

  updateTransaction: async (id, data) => {
    const txn = await api.updateTransaction(id, data);
    set((s) => ({
      transactions: s.transactions.map((t) => (t.id === id ? txn : t)),
    }));
    return txn;
  },

  deleteTransaction: async (id) => {
    await api.deleteTransaction(id);
    set((s) => ({ transactions: s.transactions.filter((t) => t.id !== id) }));
  },
}));
