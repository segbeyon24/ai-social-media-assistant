import { ReactNode, useEffect } from "react";
import { supabase } from "../lib/supabase";
import { useAuthStore } from "../state/auth";

interface Props {
  children: ReactNode;
}

export function AuthProvider({ children }: Props) {
  const hydrate = useAuthStore((s) => s.hydrate);
  const setSession = useAuthStore((s) => s.setSession);
  const clear = useAuthStore((s) => s.clear);

  useEffect(() => {
    let mounted = true;

    const init = async () => {
      // Remove OAuth hash
      if (window.location.hash.includes("access_token")) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      const { data } = await supabase.auth.getSession();
      if (!mounted) return;

      hydrate(data.session ?? null);
    };

    init();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) setSession(session);
      else clear();
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [hydrate, setSession, clear]);

  return <>{children}</>;
}
