// NodePalette.tsx — Left sidebar with draggable node items that can be dropped onto the React Flow canvas.
'use client'
import { NODE_PALETTE_ITEMS } from '@/lib/constants'

function PaletteItem({ item }: { item: typeof NODE_PALETTE_ITEMS[number] }) {
  const onDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/lakehouse-node', JSON.stringify({
      type: item.type,
      sourceType: item.sourceType,
      label: item.label,
    }))
    e.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '8px 12px',
        borderRadius: 6,
        border: '1px solid #2d3142',
        background: '#1a1d27',
        cursor: 'grab',
        userSelect: 'none',
        color: '#e2e8f0',
        fontSize: 13,
      }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = item.color)}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#2d3142')}
    >
      <span style={{ fontSize: 16, borderLeft: `3px solid ${item.color}`, paddingLeft: 6 }}>
        {item.icon}
      </span>
      <span>{item.label}</span>
    </div>
  )
}

export function NodePalette() {
  return (
    <div style={{
      width: 220,
      background: '#0f1117',
      borderRight: '1px solid #2d3142',
      padding: '16px 12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      overflowY: 'auto',
    }}>
      <div style={{ color: '#64748b', fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', marginBottom: 4 }}>
        NODES
      </div>
      {NODE_PALETTE_ITEMS.map((item) => (
        <PaletteItem key={item.label} item={item} />
      ))}
      <div style={{ marginTop: 16, color: '#64748b', fontSize: 11, lineHeight: 1.5 }}>
        Drag nodes onto the canvas to build your pipeline.
      </div>
    </div>
  )
}
