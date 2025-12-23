import { Link } from "react-router-dom";
import { useAuth } from "../../state/auth";

export default function Home() {
  const { session, loading } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-neutral-50 text-neutral-900">
      {/* Header */}
      <header className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="text-xl font-semibold tracking-tight">LeanSocial</div>
        <nav className="flex items-center gap-4">
          {!loading && session ? (
            <Link
              to="/me"
              className="rounded-xl bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 transition"
            >
              Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="rounded-xl bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 transition"
            >
              Sign in
            </Link>
          )}
        </nav>
      </header>

      {/* Hero */}
      <main className="max-w-7xl mx-auto px-6 py-24">
        <div className="max-w-3xl">
          <h1 className="text-5xl font-semibold tracking-tight leading-tight">
            Your AI co‑pilot for
            <span className="block text-neutral-500">social intelligence</span>
          </h1>

          <p className="mt-6 text-lg text-neutral-600 leading-relaxed">
            LeanSocial helps you research topics, analyze engagement, and create
            platform‑native content — all powered by your own AI keys and
            connected social accounts.
          </p>

          <div className="mt-10 flex items-center gap-4">
            <Link
              to="/login"
              className="rounded-2xl bg-neutral-900 px-6 py-3 text-base font-medium text-white hover:bg-neutral-800 transition"
            >
              Get started
            </Link>
            <a
              href="#features"
              className="text-base font-medium text-neutral-700 hover:text-neutral-900 transition"
            >
              Learn more
            </a>
          </div>
        </div>

        {/* Feature strip */}
        <section
          id="features"
          className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          <Feature
            title="AI‑powered research"
            description="Summarize trends, analyze sources, and monitor topics in real time."
          />
          <Feature
            title="Native social posting"
            description="Create and schedule posts optimized for each platform."
          />
          <Feature
            title="Private by design"
            description="Bring your own API keys. You stay in control of your data."
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-200 mt-32">
        <div className="max-w-7xl mx-auto px-6 py-10 text-sm text-neutral-500">
          © {new Date().getFullYear()} LeanSocial. Built for creators who care
          about signal, not noise.
        </div>
      </footer>
    </div>
  );
}

function Feature({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-medium">{title}</h3>
      <p className="mt-2 text-neutral-600 leading-relaxed">{description}</p>
    </div>
  );
}
