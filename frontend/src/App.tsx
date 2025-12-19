import { useEffect } from "react";
import { AppRouter } from "./AppRouter";
import { useAuthStore } from "./state/auth";
import { supabase } from "./lib/supabase";

export default function App() {
  const setSession = useAuthStore((s) => s.setSession);

  useEffect(() => {
    // Hydrate session from URL hash or storage
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session ?? null);
    });

    // Listen for future auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [setSession]);

  return <AppRouter />;
}
