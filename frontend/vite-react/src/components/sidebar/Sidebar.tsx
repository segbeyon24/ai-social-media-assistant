import React from 'react'
import { NavLink } from 'react-router-dom'

export default function Sidebar(){
  return (
    <nav className="p-4">
      <ul className="space-y-2">
        <li><NavLink to="/" end className={({isActive}) => isActive ? 'font-semibold' : ''}>Home</NavLink></li>
        <li><NavLink to="/me" className={({isActive}) => isActive ? 'font-semibold' : ''}>Dashboard</NavLink></li>
        <li><NavLink to="/login" className={({isActive}) => isActive ? 'font-semibold' : ''}>Login</NavLink></li>
      </ul>
    </nav>
  )
}
