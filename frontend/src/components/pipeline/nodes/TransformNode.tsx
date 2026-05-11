// TransformNode.tsx — Custom React Flow node for dbt model transformations with both input and output handles.
'use client'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import { useWorkspaceStore } from '@/stores/workspaceStore'

export function TransformNode({ id, data, selected }: NodeProps) {
  const setSelectedNodeId = useWorkspaceStore((s) => s.setSelectedNodeId)
  const setActiveRightPanel = useWorkspaceStore((s) => s.setActiveRightPanel)
  const color = '#a855f7'

  return (
    <div
      onClick={() => { setSelectedNodeId(id); setActiveRightPanel('config') }}
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
        <span style={{ fontSize: 18 }}>⚙️</span>
        <div>
          <div style={{ color: '#e2e8f0', fontSize: 13, fontWeight: 600 }}>
            {(data.label as string) || 'dbt Model'}
          </div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>TRANSFORM</div>
        </div>
      </div>
      <Handle type="target" position={Position.Left} style={{ background: color }} />
      <Handle type="source" position={Position.Right} style={{ background: color }} />
    </div>
  )
}
