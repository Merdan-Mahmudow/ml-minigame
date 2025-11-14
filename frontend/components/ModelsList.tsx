'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000'

interface Model {
  id: string
  name: string
  model_type: string
  description: string
  created_at: string
}

export default function ModelsList({ token }: { token: string }) {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_URL}/api/models`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setModels(data)
      }
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h2>Models</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
        {models.map((model) => (
          <div
            key={model.id}
            style={{
              padding: '1rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              backgroundColor: '#fff',
            }}
          >
            <h3>{model.name}</h3>
            <p>Type: {model.model_type}</p>
            {model.description && <p>{model.description}</p>}
            <p style={{ fontSize: '0.875rem', color: '#666' }}>
              Created: {new Date(model.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

