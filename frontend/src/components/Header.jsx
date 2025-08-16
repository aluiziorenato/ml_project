import React from 'react'

export default function Header({ currentView, setCurrentView }) {
  return (
    <header className="bg-gradient-to-r from-indigo-600 to-cyan-500 text-white p-5 shadow-md">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">ML Integration — Dashboard</h1>
          <div className="text-sm opacity-90">Conecte, teste e visualize suas integrações</div>
        </div>
        
        {/* Navigation */}
        <nav className="flex space-x-4">
          <button
            onClick={() => setCurrentView('dashboard')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'dashboard'
                ? 'bg-white text-indigo-600 font-medium'
                : 'bg-indigo-500 hover:bg-indigo-400 text-white'
            }`}
          >
            📊 Main Dashboard
          </button>
          <button
            onClick={() => setCurrentView('campaign-automation')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'campaign-automation'
                ? 'bg-white text-indigo-600 font-medium'
                : 'bg-indigo-500 hover:bg-indigo-400 text-white'
            }`}
          >
            🤖 Campaign Automation
          </button>
          <button
            onClick={() => setCurrentView('seo-intelligence')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'seo-intelligence'
                ? 'bg-white text-indigo-600 font-medium'
                : 'bg-indigo-500 hover:bg-indigo-400 text-white'
            }`}
          >
            🧠 SEO Intelligence
          </button>
        </nav>
      </div>
    </header>
  )
}
