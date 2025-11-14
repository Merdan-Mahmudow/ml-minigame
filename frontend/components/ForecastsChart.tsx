'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

interface Forecast {
  id: string
  asset_id: string
  timestamp_forecasted: string
  horizon: number
  point_forecast: number
  low_bound: number
  high_bound: number
}

export default function ForecastsChart({ token }: { token: string }) {
  const [forecasts, setForecasts] = useState<Forecast[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAsset, setSelectedAsset] = useState<string>('')

  useEffect(() => {
    if (selectedAsset) {
      fetchForecasts()
    }
  }, [selectedAsset])

  const fetchForecasts = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/forecasts/history?asset_id=${selectedAsset}&limit=100`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setForecasts(data)
      }
    } catch (error) {
      console.error('Failed to fetch forecasts:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  const chartData = forecasts.map((f) => ({
    date: new Date(f.timestamp_forecasted).toLocaleDateString(),
    forecast: f.point_forecast,
    low: f.low_bound,
    high: f.high_bound,
  }))

  return (
    <div>
      <h2>Forecasts</h2>
      <input
        type="text"
        placeholder="Asset ID"
        value={selectedAsset}
        onChange={(e) => setSelectedAsset(e.target.value)}
        style={{ padding: '0.5rem', marginBottom: '1rem', width: '300px' }}
      />
      {chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="forecast" stroke="#8884d8" name="Forecast" />
            <Line type="monotone" dataKey="low" stroke="#82ca9d" name="Low Bound" />
            <Line type="monotone" dataKey="high" stroke="#ffc658" name="High Bound" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

