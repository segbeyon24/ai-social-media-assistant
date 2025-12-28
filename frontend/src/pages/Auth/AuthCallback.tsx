import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../lib/supabase";

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const finalize = async () => {
      const { data } = await supabase.auth.getSession();

      if (data.session) {
        navigate("/me", { replace: true });
      } else {
        navigate("/login", { replace: true });
      }
    };

    finalize();
  }, [navigate]);

  return (
    <div className="flex h-screen items-center justify-center text-sm text-neutral-500">
      Signing you in…
    </div>
  );
}
