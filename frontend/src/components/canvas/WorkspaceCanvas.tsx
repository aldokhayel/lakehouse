// WorkspaceCanvas.tsx — Root layout component: node palette, React Flow canvas, resizable right panel, and status bar.
'use client'
import { useRef, useState, useCallback } from 'react'
import { ReactFlowProvider } from '@xyflow/react'
import { NodePalette } from '@/components/pipeline/sidebar/NodePalette'
import { PipelineEditor } from '@/components/pipeline/PipelineEditor'
import { NodeConfigPanel } from '@/components/pipeline/NodeConfigPanel'
import { NiFiEmbed } from '@/components/nifi/NiFiEmbed'
import { NiFiControls } from '@/components/nifi/NiFiControls'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { StatusBar } from '@/components/shared/StatusBar'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { useNiFiStatus } from '@/hooks/useNiFi'

const MIN_RIGHT_WIDTH = 260
const MAX_RIGHT_WIDTH = 700
const DEFAULT_RIGHT_WIDTH = 380

function RightPanelTabs() {
  const { activeRightPanel, setActiveRightPanel } = useWorkspaceStore()
  const tabs = [
    { id: 'config' as const, label: 'Config' },
    { id: 'nifi' as const, label: 'NiFi' },
    { id: 'chat' as const, label: 'Chat' },
  ]
  return (
    <div style={{ display: 'flex', borderBottom: '1px solid #2d3142', flexShrink: 0 }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveRightPanel(tab.id)}
          style={{
            flex: 1, padding: '9px 0', background: 'none', border: 'none',
            borderBottom: activeRightPanel === tab.id ? '2px solid #3b82f6' : '2px solid transparent',
            color: activeRightPanel === tab.id ? '#e2e8f0' : '#64748b',
            cursor: 'pointer', fontSize: 13, fontWeight: activeRightPanel === tab.id ? 600 : 400,
            transition: 'color 0.15s',
          }}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

export default function WorkspaceCanvas() {
  // Poll NiFi status every 30s
  useNiFiStatus()

  const [rightWidth, setRightWidth] = useState(DEFAULT_RIGHT_WIDTH)
  const dragging = useRef(false)
  const startX = useRef(0)
  const startWidth = useRef(DEFAULT_RIGHT_WIDTH)
  const { activeRightPanel } = useWorkspaceStore()

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    dragging.current = true
    startX.current = e.clientX
    startWidth.current = rightWidth
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [rightWidth])

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current) return
    const delta = startX.current - e.clientX
    const newWidth = Math.min(MAX_RIGHT_WIDTH, Math.max(MIN_RIGHT_WIDTH, startWidth.current + delta))
    setRightWidth(newWidth)
  }, [])

  const onMouseUp = useCallback(() => {
    dragging.current = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [])

  return (
    <div
      style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f1117' }}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
    >
      {/* Main area: palette + canvas + right panel */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left: Node Palette */}
        <NodePalette />

        {/* Center: Pipeline Editor */}
        <ReactFlowProvider>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <PipelineEditor />
          </div>
        </ReactFlowProvider>

        {/* Drag handle */}
        <div
          onMouseDown={onMouseDown}
          style={{
            width: 4, background: '#2d3142', cursor: 'col-resize', flexShrink: 0,
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = '#3b82f6')}
          onMouseLeave={(e) => (e.currentTarget.style.background = '#2d3142')}
        />

        {/* Right: Contextual Panel */}
        <div style={{
          width: rightWidth, background: '#0f1117',
          borderLeft: '1px solid #2d3142',
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden', flexShrink: 0,
        }}>
          <RightPanelTabs />
          <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            {activeRightPanel === 'config' && <NodeConfigPanel />}
            {activeRightPanel === 'nifi' && (
              <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
                <div style={{ flex: 1, overflow: 'hidden' }}><NiFiEmbed /></div>
                <NiFiControls />
              </div>
            )}
            {activeRightPanel === 'chat' && <ChatPanel />}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <StatusBar />
    </div>
  )
}
