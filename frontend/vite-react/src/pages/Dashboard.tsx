import React from 'react'
import MetricCard from '../components/cards/MetricCard'

export default function Dashboard() {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard title="Followers" value="—" />
        <MetricCard title="Engagement" value="—" />
        <MetricCard title="Reach" value="—" />
      </div>
    </div>
  )
}
