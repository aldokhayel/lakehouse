// StatusBar.tsx — Fixed 32px bottom bar showing live service health, pipeline status, and Grafana link.
'use client'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { usePipelineStore } from '@/stores/pipelineStore'
import { useServiceHealth } from '@/hooks/useServiceHealth'
import { GRAFANA_URL } from '@/lib/constants'

const DOT_COLOR: Record<string, string> = {
  ok: '#10b981', healthy: '#10b981', degraded: '#f59e0b',
  error: '#ef4444', unknown: '#64748b',
  idle: '#64748b', running: '#f59e0b', success: '#10b981',
}

const SERVICE_LABELS: Record<string, string> = {
  backend: 'API', trino: 'Trino', minio: 'MinIO', chromadb: 'VectorDB', vanna: 'AI',
}

export function StatusBar() {
  useServiceHealth()

  const { pipelineStatus, lastQueryInfo, serviceHealth } = useWorkspaceStore()
  const pipelineName = usePipelineStore((s) => s.pipelineName)

  const serviceEntries = Object.entries(SERVICE_LABELS).filter(
    ([key]) => serviceHealth[key] !== undefined
  )

  return (
    <div style={{
      height: 32, background: '#1a1d27', borderTop: '1px solid #2d3142',
      display: 'flex', alignItems: 'center', padding: '0 16px',
      gap: 20, fontSize: 11, color: '#64748b', flexShrink: 0, overflow: 'hidden',
    }}>
      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <span style={{ color: DOT_COLOR[pipelineStatus] ?? '#64748b' }}>●</span>
        <span>Pipeline: <span style={{ color: '#94a3b8' }}>{pipelineStatus}</span></span>
      </span>

      {serviceEntries.map(([key, label]) => {
        const s = serviceHealth[key] ?? 'unknown'
        return (
          <span key={key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ color: DOT_COLOR[s] ?? '#64748b' }}>●</span>
            <span style={{ color: s === 'ok' ? '#94a3b8' : s === 'error' ? '#fca5a5' : '#fde68a' }}>{label}</span>
          </span>
        )
      })}

      {lastQueryInfo && (
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ color: '#3b82f6' }}>◆</span>
          <span style={{ color: '#94a3b8' }}>{lastQueryInfo}</span>
        </span>
      )}

      <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
        <a href={GRAFANA_URL} target="_blank" rel="noopener noreferrer"
          style={{ color: '#f97316', textDecoration: 'none', fontSize: 11 }}>
          📊 Metrics
        </a>
        <span style={{ color: '#2d3142' }}>{pipelineName} · Lakehouse v0.1</span>
      </span>
    </div>
  )
}
