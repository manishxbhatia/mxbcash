import { create } from "zustand";
import type { Account, AccountTreeNode, Commodity } from "../types";
import * as api from "../api";

interface AccountState {
  accounts: Account[];
  tree: AccountTreeNode[];
  commodities: Commodity[];
  loading: boolean;
  error: string | null;

  fetchAccounts: () => Promise<void>;
  fetchTree: () => Promise<void>;
  fetchCommodities: () => Promise<void>;
  createAccount: (data: Omit<Account, "id" | "full_name">) => Promise<Account>;
  updateAccount: (id: number, data: Partial<Account>) => Promise<Account>;
  deleteAccount: (id: number) => Promise<void>;
}

export const useAccountStore = create<AccountState>((set) => ({
  accounts: [],
  tree: [],
  commodities: [],
  loading: false,
  error: null,

  fetchAccounts: async () => {
    set({ loading: true, error: null });
    try {
      const accounts = await api.getAccounts();
      set({ accounts, loading: false });
    } catch (e) {
      set({ error: String(e), loading: false });
    }
  },

  fetchTree: async () => {
    set({ loading: true, error: null });
    try {
      const tree = await api.getAccountTree();
      set({ tree, loading: false });
    } catch (e) {
      set({ error: String(e), loading: false });
    }
  },

  fetchCommodities: async () => {
    try {
      const commodities = await api.getCommodities();
      set({ commodities });
    } catch (e) {
      set({ error: String(e) });
    }
  },

  createAccount: async (data) => {
    const account = await api.createAccount(data);
    set((s) => ({ accounts: [...s.accounts, account] }));
    return account;
  },

  updateAccount: async (id, data) => {
    const account = await api.updateAccount(id, data);
    set((s) => ({
      accounts: s.accounts.map((a) => (a.id === id ? account : a)),
    }));
    return account;
  },

  deleteAccount: async (id) => {
    await api.deleteAccount(id);
    set((s) => ({ accounts: s.accounts.filter((a) => a.id !== id) }));
  },
}));
