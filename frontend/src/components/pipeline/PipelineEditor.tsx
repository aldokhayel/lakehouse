// PipelineEditor.tsx — Main React Flow canvas with drag-and-drop node creation, toolbar, and Zustand sync.
'use client'
import { useCallback, useRef } from 'react'
import {
  ReactFlow, Background, Controls, MiniMap, BackgroundVariant,
  useNodesState, useEdgesState, addEdge,
  type Node, type Edge, type OnConnect, type ReactFlowInstance,
} from '@xyflow/react'
import { usePipelineStore } from '@/stores/pipelineStore'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { useSavePipeline, useRunPipeline } from '@/hooks/usePipeline'
import { SourceNode } from './nodes/SourceNode'
import { TransformNode } from './nodes/TransformNode'
import { DestinationNode } from './nodes/DestinationNode'
import { NiFiFlowNode } from './nodes/NiFiFlowNode'

const nodeTypes = {
  source: SourceNode,
  transform: TransformNode,
  destination: DestinationNode,
  nifi_flow: NiFiFlowNode,
}

let nodeIdCounter = 1
function newId() { return `node_${nodeIdCounter++}` }

export function PipelineEditor() {
  const rfInstance = useRef<ReactFlowInstance | null>(null)
  const { pipelineName, setPipelineName, setNodes: storeSetNodes, setEdges: storeSetEdges, isDirty } = usePipelineStore()
  const { setPipelineStatus } = useWorkspaceStore()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const saveMutation = useSavePipeline()
  const runMutation = useRunPipeline()

  const onConnect: OnConnect = useCallback((params) => {
    setEdges((eds) => {
      const updated = addEdge({ ...params, style: { stroke: '#3b82f6' }, animated: true }, eds)
      storeSetEdges(updated)
      return updated
    })
  }, [setEdges, storeSetEdges])

  const onNodesChangeWrapped: typeof onNodesChange = useCallback((changes) => {
    onNodesChange(changes)
    // sync to store after applying changes — use setTimeout to get updated state
    setTimeout(() => storeSetNodes(nodes), 0)
  }, [onNodesChange, nodes, storeSetNodes])

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const raw = e.dataTransfer.getData('application/lakehouse-node')
    if (!raw || !rfInstance.current) return
    const { type, sourceType, label } = JSON.parse(raw)
    const position = rfInstance.current.screenToFlowPosition({ x: e.clientX, y: e.clientY })
    const newNode: Node = {
      id: newId(),
      type,
      position,
      data: { label, sourceType },
    }
    setNodes((nds) => {
      const updated = [...nds, newNode]
      storeSetNodes(updated)
      return updated
    })
  }, [setNodes, storeSetNodes])

  const handleSave = async () => {
    storeSetNodes(nodes)
    storeSetEdges(edges)
    saveMutation.mutate()
  }

  const handleRun = () => runMutation.mutate()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%' }}>
      {/* Toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '8px 16px',
        background: '#1a1d27',
        borderBottom: '1px solid #2d3142',
        flexShrink: 0,
      }}>
        <input
          value={pipelineName}
          onChange={(e) => setPipelineName(e.target.value)}
          style={{
            background: 'transparent', border: 'none', outline: 'none',
            color: '#e2e8f0', fontSize: 14, fontWeight: 600,
            flex: 1, maxWidth: 280,
          }}
          placeholder="Pipeline name..."
        />
        {isDirty && <span style={{ color: '#64748b', fontSize: 12 }}>unsaved changes</span>}
        <button
          onClick={handleSave}
          disabled={saveMutation.isPending}
          style={{
            background: '#2d3142', border: 'none', borderRadius: 6,
            color: '#e2e8f0', padding: '6px 14px', fontSize: 13,
            cursor: 'pointer', opacity: saveMutation.isPending ? 0.5 : 1,
          }}
        >
          {saveMutation.isPending ? 'Saving…' : 'Save'}
        </button>
        <button
          onClick={handleRun}
          disabled={runMutation.isPending}
          style={{
            background: '#10b981', border: 'none', borderRadius: 6,
            color: 'white', padding: '6px 14px', fontSize: 13,
            cursor: 'pointer', fontWeight: 600,
            opacity: runMutation.isPending ? 0.7 : 1,
          }}
        >
          {runMutation.isPending ? 'Running…' : '▶ Run Pipeline'}
        </button>
      </div>

      {/* Canvas */}
      <div style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChangeWrapped}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onInit={(inst) => { rfInstance.current = inst }}
          fitView
          defaultEdgeOptions={{ style: { stroke: '#3b82f6' }, animated: true }}
          style={{ background: '#0f1117' }}
          deleteKeyCode="Delete"
        >
          <Background variant={BackgroundVariant.Dots} color="#2d3142" gap={24} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(n) => {
              const colors: Record<string, string> = { source: '#3b82f6', transform: '#a855f7', destination: '#10b981', nifi_flow: '#0ea5e9' }
              return colors[n.type ?? ''] ?? '#64748b'
            }}
            maskColor="rgba(15,17,23,0.8)"
          />
        </ReactFlow>
      </div>
    </div>
  )
}
