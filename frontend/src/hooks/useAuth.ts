import { useEffect } from "react";
import { supabase } from "../lib/supabase";
import { useAuthStore } from "../state/auth";

export function useAuth() {
  const { session, user, isAuthenticated, isLoading, setSession, clear } =
    useAuthStore();

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session ?? null);
    });

    const { data } = supabase.auth.onAuthStateChange((_e, session) => {
      setSession(session);
    });

    return () => {
      data.subscription.unsubscribe();
    };
  }, [setSession]);

  return {
    session,
    user,
    isAuthenticated,
    isLoading,
    logout: async () => {
      await supabase.auth.signOut();
      clear();
    },
  };
}
