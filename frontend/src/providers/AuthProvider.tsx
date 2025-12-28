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

    const bootstrapAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!mounted) return;

      // 🔑 THIS IS THE CRITICAL LINE
      hydrate(session ?? null);
    };

    bootstrapAuth();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!mounted) return;

      if (session) {
        setSession(session); // loading already false
      } else {
        clear();
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [hydrate, setSession, clear]);

  return <>{children}</>;
}
