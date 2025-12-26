import { ReactNode, useEffect } from "react";
import { supabase } from "../lib/supabase";
import { useAuthStore } from "../state/auth";

interface Props {
  children: ReactNode;
}

export function AuthProvider({ children }: Props) {
  const setSession = useAuthStore((s) => s.setSession);
  const clear = useAuthStore((s) => s.clear);

  useEffect(() => {
    let mounted = true;

    const initAuth = async () => {
      // 1️⃣ Handle OAuth hash once (CRITICAL FIX)
      if (window.location.hash.includes("access_token")) {
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );
      }

      // 2️⃣ Hydrate existing session (storage or OAuth)
      const { data } = await supabase.auth.getSession();
      if (!mounted) return;

      setSession(data.session ?? null);
    };

    initAuth();

    // 3️⃣ Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setSession(session);
      } else {
        clear();
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [setSession, clear]);

  return <>{children}</>;
}
