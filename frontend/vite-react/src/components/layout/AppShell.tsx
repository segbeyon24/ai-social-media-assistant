import React from 'react'
import { Outlet, Link } from 'react-router-dom'
import Sidebar from '../sidebar/Sidebar'

export default function AppShell(){
  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-64 bg-white border-r"><Sidebar /></aside>
      <div className="flex-1">
        <header className="p-4 border-b bg-white">
          <div className="max-w-6xl mx-auto">LeanSocial</div>
        </header>
        <main className="max-w-6xl mx-auto p-4">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
