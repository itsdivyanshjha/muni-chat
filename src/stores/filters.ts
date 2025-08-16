import { create } from 'zustand';
import { Filters } from '@/lib/types';

interface FiltersStore {
  filters: Filters;
  setTimeRange: (from: string | null, to: string | null) => void;
  setWard: (ward: string | null) => void;
  setZone: (zone: string | null) => void;
  setCategory: (category: string | null) => void;
  clearAll: () => void;
  updateFilters: (newFilters: Partial<Filters>) => void;
}

const defaultFilters: Filters = {
  time: { from: null, to: null },
  place: { ward: null, zone: null },
  extra: { category: null }
};

export const useFilters = create<FiltersStore>((set) => ({
  filters: defaultFilters,
  
  setTimeRange: (from, to) =>
    set((state) => ({
      filters: {
        ...state.filters,
        time: { from, to }
      }
    })),
  
  setWard: (ward) =>
    set((state) => ({
      filters: {
        ...state.filters,
        place: { ...state.filters.place, ward }
      }
    })),
  
  setZone: (zone) =>
    set((state) => ({
      filters: {
        ...state.filters,
        place: { ...state.filters.place, zone }
      }
    })),
  
  setCategory: (category) =>
    set((state) => ({
      filters: {
        ...state.filters,
        extra: { category }
      }
    })),
  
  clearAll: () => set({ filters: defaultFilters }),
  
  updateFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters }
    }))
}));