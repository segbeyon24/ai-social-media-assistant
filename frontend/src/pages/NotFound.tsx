import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="text-center">
        <h1 className="text-6xl font-semibold tracking-tight">404</h1>
        <p className="mt-4 text-neutral-600">This page doesn’t exist.</p>
        <Link
          to="/"
          className="mt-6 inline-block rounded-xl bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 transition"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
