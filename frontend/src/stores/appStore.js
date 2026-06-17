import { create } from "zustand";

const useAppStore = create((set) => ({
  selectedTable: null,
  setSelectedTable: (tableName) => set({ selectedTable: tableName }),

  chatHistory: [],
  addChatMessage: (message) =>
    set((state) => ({ chatHistory: [...state.chatHistory, message] })),
  clearChatHistory: () => set({ chatHistory: [] }),
}));

export default useAppStore;
