import { useEffect, useState } from "react";
import { api } from "../lib/api";
import AppShell from "../components/layout/AppShell";
import { MetricCard } from "../components/layout/cards/MetricCard";

interface Overview {
  connected_accounts: number;
  scheduled_posts: number;
  total_engagement: number;
}

export default function Dashboard() {
  const [data, setData] = useState<Overview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get("/me");
        setData(res.data);
      } catch (e) {
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <AppShell>
      <div className="space-y-8">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-neutral-600">
            Overview of your connected platforms and activity
          </p>
        </header>

        {loading && (
          <div className="text-neutral-500">Loading insights…</div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {data && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              label="Connected accounts"
              value={data.connected_accounts.toString()}
            />
            <MetricCard
              label="Scheduled posts"
              value={data.scheduled_posts.toString()}
            />
            <MetricCard
              label="Total engagement"
              value={data.total_engagement.toString()}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
}
