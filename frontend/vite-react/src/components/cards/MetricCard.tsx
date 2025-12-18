import React from 'react'

export default function MetricCard({title, value}:{title:string; value:string}){
  return (
    <div className="p-4 bg-white rounded shadow">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="mt-2 text-2xl font-bold">{value}</div>
    </div>
  )
}
