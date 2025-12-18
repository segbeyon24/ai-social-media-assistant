import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Home from '../pages/Home'
import Dashboard from '../pages/Dashboard'
import Login from '../pages/Login'
import NotFound from '../pages/NotFound'
import AppShell from '../components/layout/AppShell'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}> 
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="me" element={<Dashboard />} />
        <Route path="*" element={<NotFound />} />
      </Route>
      <Route path="/app/*" element={<Navigate to="/me" replace />} />
    </Routes>
  )
}
