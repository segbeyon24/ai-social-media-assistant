import React from 'react'

export default function Login() {
  const handleSupabase = () => {
    // Redirect user to backend Supabase OAuth start
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    window.location.href = `${base}/auth/supabase/login`
  }

  return (
    <div className="p-6 max-w-md">
      <h2 className="text-2xl font-semibold">Login</h2>
      <p className="mt-2 text-gray-600">Sign in to manage your platforms.</p>
      <div className="mt-4">
        <button onClick={handleSupabase} className="px-4 py-2 bg-blue-600 text-white rounded">Sign in</button>
      </div>
    </div>
  )
}
