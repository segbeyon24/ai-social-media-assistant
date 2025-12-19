import { useEffect } from "react";
import { AppRouter } from "./AppRouter";
import { useAuthStore } from "./state/auth";
import { supabase } from "./lib/supabase";

export default function App() {
  const setSession = useAuthStore((s) => s.setSession);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session ?? null);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [setSession]);

  return <AppRouter />;
}
