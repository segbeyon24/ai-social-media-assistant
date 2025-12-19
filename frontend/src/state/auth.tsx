import { create } from "zustand";
import type { Session, User } from "@supabase/supabase-js";

interface AuthState {
  session: Session | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  setSession: (session: Session | null) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setSession: (session) =>
    set({
      session,
      user: session?.user ?? null,
      isAuthenticated: Boolean(session),
      isLoading: false,
    }),

  clear: () =>
    set({
      session: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),
}));

/**
 * Public auth hook used by pages/components
 * This is what you import everywhere.
 */
export function useAuth() {
  const {
    session,
    user,
    isAuthenticated,
    isLoading,
    setSession,
    clear,
  } = useAuthStore();

  return {
    session,
    user,
    isAuthenticated,
    isLoading,
    setSession,
    logout: clear,
  };
}
