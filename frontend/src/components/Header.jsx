import React from 'react'

export default function Header(){
  return (
    <header className="bg-gradient-to-r from-indigo-600 to-cyan-500 text-white p-5 shadow-md">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <h1 className="text-2xl font-bold">ML Integration — Dashboard</h1>
        <div className="text-sm opacity-90">Conecte, teste e visualize suas integrações Mercado Libre</div>
      </div>
    </header>
  )
}
