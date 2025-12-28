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

    const init = async () => {
      // 🔑 Remove OAuth hash safely
      if (window.location.hash.includes("access_token")) {
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );
      }

      // 🔑 Hydrate session ONCE
      const { data } = await supabase.auth.getSession();
      if (!mounted) return;

      setSession(data.session ?? null);
    };

    init();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!mounted) return;
      session ? setSession(session) : clear();
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [setSession, clear]);

  return <>{children}</>;
}
