import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";
import { useAuth } from "../../state/auth";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const { session, isLoading } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && session) {
      navigate("/me", { replace: true });
    }
  }, [session, isLoading, navigate]);

  const signInWithGoogle = async () => {
    setError(null);

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
,
      },
    });

    if (error) {
      setError(error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold tracking-tight">
          Welcome back
        </h1>

        <p className="mt-2 text-neutral-600">
          Sign in to continue to LeanSocial
        </p>

        <div className="mt-8 space-y-4">
          <button
            onClick={signInWithGoogle}
            className="w-full rounded-xl border border-neutral-300 px-4 py-3 text-sm font-medium transition hover:bg-neutral-50"
          >
            Continue with Google
          </button>

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
        </div>

        <p className="mt-8 text-xs text-neutral-500">
          New here?{" "}
          <Link
            to="/signup"
            className="underline underline-offset-2 hover:text-neutral-700"
          >
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
