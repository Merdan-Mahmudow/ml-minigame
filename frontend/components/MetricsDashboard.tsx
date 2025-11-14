'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

interface Metrics {
  mae: number
  rmse: number
  mape: number
  coverage?: number
}

export default function MetricsDashboard({ token }: { token: string }) {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [assetId, setAssetId] = useState<string>('')

  const fetchMetrics = async () => {
    if (!assetId) return
    setLoading(true)
    try {
      const response = await fetch(
        `${API_URL}/api/admin/monitoring/metrics/${assetId}/summary`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setMetrics(data.metrics)
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !metrics) return <div>Loading...</div>

  return (
    <div>
      <h2>Metrics Dashboard</h2>
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Asset ID"
          value={assetId}
          onChange={(e) => setAssetId(e.target.value)}
          style={{ padding: '0.5rem', marginRight: '0.5rem' }}
        />
        <button onClick={fetchMetrics} style={{ padding: '0.5rem 1rem' }}>
          Load Metrics
        </button>
      </div>
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}>
            <h3>MAE</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.mae.toFixed(2)}</p>
          </div>
          <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}>
            <h3>RMSE</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.rmse.toFixed(2)}</p>
          </div>
          <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}>
            <h3>MAPE</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.mape.toFixed(2)}%</p>
          </div>
          {metrics.coverage && (
            <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}>
              <h3>Coverage</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.coverage.toFixed(2)}%</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

