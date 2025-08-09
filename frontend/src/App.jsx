import React from 'react'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import ApiConfig from './pages/ApiConfig'
import OAuthManager from './pages/OAuthManager'
import ApiTester from './pages/ApiTester'

export default function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="p-6">
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
      </main>
    </div>
  )
}
