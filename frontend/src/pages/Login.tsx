import { useEffect } from "react";
import { supabase } from "../lib/supabase";
import { useAuth } from "../state/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { session, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && session) {
      navigate("/me", { replace: true });
    }
  }, [session, loading, navigate]);

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}`,
      },
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold tracking-tight">
          Welcome back
        </h1>
        <p className="mt-2 text-neutral-600">
          Sign in to your LeanSocial workspace
        </p>

        <div className="mt-8">
          <button
            onClick={signInWithGoogle}
            className="w-full rounded-xl border border-neutral-300 px-4 py-3 text-sm font-medium hover:bg-neutral-50 transition"
          >
            Continue with Google
          </button>
        </div>

        <p className="mt-8 text-xs text-neutral-500 leading-relaxed">
          By continuing, you agree to LeanSocial’s Terms of Service and Privacy
          Policy.
        </p>
      </div>
    </div>
  );
}
