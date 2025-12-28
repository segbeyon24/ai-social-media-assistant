import { create } from "zustand";
import type { Session, User } from "@supabase/supabase-js";

interface AuthState {
  session: Session | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  hydrate: (session: Session | null) => void;
  setSession: (session: Session | null) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  user: null,
  isAuthenticated: false,
  isLoading: true,

  // 🔑 ONLY called once on app start
  hydrate: (session) =>
    set({
      session,
      user: session?.user ?? null,
      isAuthenticated: Boolean(session),
      isLoading: false,
    }),

  // 🔄 Called on auth changes AFTER hydration
  setSession: (session) =>
    set((state) => ({
      session,
      user: session?.user ?? null,
      isAuthenticated: Boolean(session),
      isLoading: state.isLoading, // 👈 DO NOT TOUCH loading here
    })),

  clear: () =>
    set({
      session: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),
}));

export function useAuth() {
  const {
    session,
    user,
    isAuthenticated,
    isLoading,
    hydrate,
    clear,
  } = useAuthStore();

  return {
    session,
    user,
    isAuthenticated,
    isLoading,
    hydrate,
    logout: clear,
  };
}
