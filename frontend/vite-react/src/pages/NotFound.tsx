import React from 'react'
import { Link } from 'react-router-dom'

export default function NotFound(){
  return (
    <div className="p-8">
      <h2 className="text-2xl">404 — Not Found</h2>
      <p className="mt-2"><Link to="/">Go home</Link></p>
    </div>
  )
}
