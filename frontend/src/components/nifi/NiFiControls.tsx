// NiFiControls.tsx — Compact start/stop controls for NiFi process group flows in the right panel.
'use client'
import { useState } from 'react'
import { useStartFlow, useStopFlow } from '@/hooks/useNiFi'
import { usePipelineStore } from '@/stores/pipelineStore'

export function NiFiControls() {
  const nodeConfigs = usePipelineStore((s) => s.nodeConfigs)
  // Find first nifi_flow node's flowId from configs
  const flowId = Object.values(nodeConfigs).find((c) => c.flowId)?.flowId ?? ''
  const [customFlowId, setCustomFlowId] = useState('')
  const targetId = customFlowId || flowId
  const startMutation = useStartFlow(targetId)
  const stopMutation = useStopFlow(targetId)

  return (
    <div style={{ padding: '12px 16px', borderTop: '1px solid #2d3142' }}>
      <div style={{ color: '#64748b', fontSize: 11, fontWeight: 700, marginBottom: 8 }}>FLOW CONTROLS</div>
      <input
        value={customFlowId}
        onChange={(e) => setCustomFlowId(e.target.value)}
        placeholder={flowId || 'Process group UUID…'}
        style={{ width: '100%', background: '#0f1117', border: '1px solid #2d3142', borderRadius: 6, padding: '6px 10px', color: '#e2e8f0', fontSize: 12, marginBottom: 8 }}
      />
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={() => startMutation.mutate()} disabled={!targetId || startMutation.isPending}
          style={{ flex: 1, background: '#10b981', border: 'none', borderRadius: 6, color: 'white', padding: '6px 0', fontSize: 12, cursor: 'pointer' }}>
          ▶ Start
        </button>
        <button onClick={() => stopMutation.mutate()} disabled={!targetId || stopMutation.isPending}
          style={{ flex: 1, background: '#ef4444', border: 'none', borderRadius: 6, color: 'white', padding: '6px 0', fontSize: 12, cursor: 'pointer' }}>
          ■ Stop
        </button>
      </div>
    </div>
  )
}
