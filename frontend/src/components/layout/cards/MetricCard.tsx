import { motion } from "framer-motion";
import { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  delta?: string;
  icon?: ReactNode;
}

export function MetricCard({ label, value, delta, icon }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="rounded-2xl bg-white/70 dark:bg-zinc-900/70 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/60 shadow-sm p-5"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
          {label}
        </span>
        {icon && <div className="text-zinc-400">{icon}</div>}
      </div>

      <div className="mt-3 flex items-end justify-between">
        <span className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
          {value}
        </span>
        {delta && (
          <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400">
            {delta}
          </span>
        )}
      </div>
    </motion.div>
  );
}
