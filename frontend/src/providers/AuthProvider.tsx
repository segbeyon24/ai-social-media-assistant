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
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session ?? null);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (session) setSession(session);
        else clear();
      }
    );

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [setSession, clear]);

  return <>{children}</>;
}
