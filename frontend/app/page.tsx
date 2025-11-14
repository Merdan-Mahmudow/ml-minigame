'use client'

import { useState, useEffect } from 'react'
import AssetsList from '@/components/AssetsList'
import ForecastsChart from '@/components/ForecastsChart'
import ModelsList from '@/components/ModelsList'
import MetricsDashboard from '@/components/MetricsDashboard'

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

export default function Home() {
  const [activeTab, setActiveTab] = useState('assets')
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Проверка токена в localStorage
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      setToken(storedToken)
    }
  }, [])

  const handleLogin = async (username: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
      })
      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('auth_token', data.access_token)
        setToken(data.access_token)
      }
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  if (!token) {
    return (
      <div style={{ padding: '2rem', maxWidth: '400px', margin: '0 auto' }}>
        <h1>Login</h1>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            const formData = new FormData(e.currentTarget)
            handleLogin(
              formData.get('username') as string,
              formData.get('password') as string
            )
          }}
        >
          <input
            name="username"
            placeholder="Username"
            required
            style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            required
            style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
          />
          <button type="submit" style={{ width: '100%', padding: '0.5rem' }}>
            Login
          </button>
        </form>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <header style={{ backgroundColor: '#fff', padding: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1>Forecast Admin Panel</h1>
        <nav style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
          {['assets', 'forecasts', 'models', 'metrics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '0.5rem 1rem',
                border: 'none',
                backgroundColor: activeTab === tab ? '#0070f3' : '#f0f0f0',
                color: activeTab === tab ? '#fff' : '#000',
                cursor: 'pointer',
                borderRadius: '4px',
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </header>

      <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        {activeTab === 'assets' && <AssetsList token={token} />}
        {activeTab === 'forecasts' && <ForecastsChart token={token} />}
        {activeTab === 'models' && <ModelsList token={token} />}
        {activeTab === 'metrics' && <MetricsDashboard token={token} />}
      </main>
    </div>
  )
}

