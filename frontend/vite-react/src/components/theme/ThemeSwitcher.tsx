import React from 'react'

export default function ThemeSwitcher(){
  return (
    <div className="p-2">
      <label className="flex items-center gap-2">
        <input type="checkbox" />
        <span>Dark</span>
      </label>
    </div>
  )
}
