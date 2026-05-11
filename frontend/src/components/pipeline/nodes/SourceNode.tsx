// SourceNode.tsx — Custom React Flow node for data source types: API, MSSQL, PostgreSQL, MongoDB.
'use client'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import { useWorkspaceStore } from '@/stores/workspaceStore'

const SOURCE_COLORS: Record<string, string> = {
  api: '#3b82f6', mssql: '#f97316', postgresql: '#06b6d4', mongodb: '#22c55e',
}
const SOURCE_ICONS: Record<string, string> = {
  api: '🔌', mssql: '🗄️', postgresql: '🐘', mongodb: '🍃',
}
const SOURCE_LABELS: Record<string, string> = {
  api: 'API Source', mssql: 'MSSQL Source', postgresql: 'PostgreSQL Source', mongodb: 'MongoDB Source',
}

export function SourceNode({ id, data, selected }: NodeProps) {
  const setSelectedNodeId = useWorkspaceStore((s) => s.setSelectedNodeId)
  const setActiveRightPanel = useWorkspaceStore((s) => s.setActiveRightPanel)
  const sourceType = (data.sourceType as string) ?? 'api'
  const color = SOURCE_COLORS[sourceType] ?? '#3b82f6'

  const handleClick = () => {
    setSelectedNodeId(id)
    setActiveRightPanel('config')
  }

  return (
    <div
      onClick={handleClick}
      style={{
        background: '#1a1d27',
        border: `1px solid ${selected ? color : '#2d3142'}`,
        borderLeft: `4px solid ${color}`,
        borderRadius: 8,
        padding: '10px 14px',
        minWidth: 160,
        cursor: 'pointer',
        boxShadow: selected ? `0 0 0 2px ${color}33` : 'none',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 18 }}>{SOURCE_ICONS[sourceType]}</span>
        <div>
          <div style={{ color: '#e2e8f0', fontSize: 13, fontWeight: 600 }}>
            {(data.label as string) || SOURCE_LABELS[sourceType]}
          </div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>
            {sourceType.toUpperCase()}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} style={{ background: color }} />
    </div>
  )
}
