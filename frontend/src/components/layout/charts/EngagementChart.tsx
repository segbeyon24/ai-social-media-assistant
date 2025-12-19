import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface EngagementPoint {
  date: string;
  value: number;
}

interface EngagementChartProps {
  title?: string;
  data: EngagementPoint[];
}

export function EngagementChart({ title = "Engagement", data }: EngagementChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="rounded-2xl bg-white/70 dark:bg-zinc-900/70 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/60 shadow-sm p-5"
    >
      <h3 className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-4">
        {title}
      </h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              stroke="#a1a1aa"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#a1a1aa"
            />
            <Tooltip
              contentStyle={{
                background: "rgba(24,24,27,0.9)",
                borderRadius: 12,
                border: "none",
                color: "#fff",
              }}
              labelStyle={{ color: "#e4e4e7" }}
            />
            <Line
              type="monotone"
              dataKey="value"
              strokeWidth={3}
              dot={false}
              stroke="currentColor"
              className="text-zinc-900 dark:text-zinc-100"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
