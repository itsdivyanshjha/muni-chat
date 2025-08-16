import { create } from 'zustand';
import { HistoryItem } from '@/lib/types';

interface HistoryStore {
  items: HistoryItem[];
  currentItem: HistoryItem | null;
  addItem: (item: HistoryItem) => void;
  setCurrentItem: (item: HistoryItem | null) => void;
  clearHistory: () => void;
}

export const useHistory = create<HistoryStore>((set) => ({
  items: [],
  currentItem: null,
  
  addItem: (item) =>
    set((state) => ({
      items: [item, ...state.items.slice(0, 49)], // Keep last 50 items
      currentItem: item
    })),
  
  setCurrentItem: (item) => set({ currentItem: item }),
  
  clearHistory: () => set({ items: [], currentItem: null })
}));