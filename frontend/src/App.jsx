import React, { useState } from 'react'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import ApiConfig from './pages/ApiConfig'
import OAuthManager from './pages/OAuthManager'
import ApiTester from './pages/ApiTester'
import SEOIntelligenceDashboard from './pages/SEOIntelligenceDashboard'
import AnunciosPage from './pages/AnunciosPage'

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard')

  const renderCurrentView = () => {
    switch (currentView) {
      case 'anuncios':
        return <AnunciosPage />
      case 'seo-intelligence':
        return <SEOIntelligenceDashboard />
      case 'dashboard':
      default:
        return (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Dashboard />
              </div>
              <div>
                <ApiConfig />
                <OAuthManager />
              </div>
            </div>
            <div className="mt-8">
              <ApiTester />
            </div>
          </>
        )
    }
  }

  return (
    <div className="min-h-screen">
      <Header currentView={currentView} setCurrentView={setCurrentView} />
      <main className="p-6">
        {renderCurrentView()}
      </main>
    </div>
  )
}
