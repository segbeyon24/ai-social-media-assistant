import React from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-3xl font-semibold">LeanSocial</h1>
      <p className="mt-4 text-gray-600">AI-assisted social media control plane.</p>
      <div className="mt-6">
        <Link to="/login" className="text-blue-600 underline">Login</Link>
      </div>
    </main>
  )
}
