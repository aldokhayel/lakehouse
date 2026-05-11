// pipelineStore.ts — Zustand store for pipeline canvas state: nodes, edges, configs, and dirty tracking.
'use client'
import { create } from 'zustand'
import type { Node, Edge } from '@xyflow/react'
import { DEFAULT_PIPELINE_NAME } from '@/lib/constants'

interface PipelineStore {
  nodes: Node[]
  edges: Edge[]
  pipelineId: string | null
  pipelineName: string
  nodeConfigs: Record<string, Record<string, string>>
  isDirty: boolean
  setNodes: (nodes: Node[] | ((prev: Node[]) => Node[])) => void
  setEdges: (edges: Edge[] | ((prev: Edge[]) => Edge[])) => void
  setPipelineId: (id: string | null) => void
  setPipelineName: (name: string) => void
  updateNodeConfig: (nodeId: string, config: Record<string, string>) => void
  markClean: () => void
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  nodes: [],
  edges: [],
  pipelineId: null,
  pipelineName: DEFAULT_PIPELINE_NAME,
  nodeConfigs: {},
  isDirty: false,
  setNodes: (nodes) =>
    set((s) => ({ nodes: typeof nodes === 'function' ? nodes(s.nodes) : nodes, isDirty: true })),
  setEdges: (edges) =>
    set((s) => ({ edges: typeof edges === 'function' ? edges(s.edges) : edges, isDirty: true })),
  setPipelineId: (id) => set({ pipelineId: id }),
  setPipelineName: (name) => set({ pipelineName: name, isDirty: true }),
  updateNodeConfig: (nodeId, config) =>
    set((s) => ({ nodeConfigs: { ...s.nodeConfigs, [nodeId]: config }, isDirty: true })),
  markClean: () => set({ isDirty: false }),
}))
