'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

interface Asset {
  id: string
  ticker: string
  name: string
  asset_type: string
  source: string
  created_at: string
}

export default function AssetsList({ token }: { token: string }) {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const response = await fetch(`${API_URL}/api/assets`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setAssets(data)
      }
    } catch (error) {
      console.error('Failed to fetch assets:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h2>Assets</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0' }}>
            <th style={{ padding: '0.5rem', textAlign: 'left' }}>Ticker</th>
            <th style={{ padding: '0.5rem', textAlign: 'left' }}>Name</th>
            <th style={{ padding: '0.5rem', textAlign: 'left' }}>Type</th>
            <th style={{ padding: '0.5rem', textAlign: 'left' }}>Source</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((asset) => (
            <tr key={asset.id}>
              <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{asset.ticker}</td>
              <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{asset.name}</td>
              <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{asset.asset_type}</td>
              <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{asset.source || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

