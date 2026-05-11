// workspaceStore.ts — Zustand store for global workspace UI state: active panel, selected node, and service statuses.
'use client'
import { create } from 'zustand'

type RightPanel = 'config' | 'nifi' | 'chat'
type PipelineStatus = 'idle' | 'running' | 'success' | 'error'
type ServiceStatus = 'unknown' | 'healthy' | 'error'

interface WorkspaceStore {
  activeRightPanel: RightPanel
  selectedNodeId: string | null
  pipelineStatus: PipelineStatus
  nifiStatus: ServiceStatus
  lastQueryInfo: string | null
  serviceHealth: Record<string, string>
  setActiveRightPanel: (panel: RightPanel) => void
  setSelectedNodeId: (id: string | null) => void
  setPipelineStatus: (status: PipelineStatus) => void
  setNifiStatus: (status: ServiceStatus) => void
  setLastQueryInfo: (info: string | null) => void
  setServiceHealth: (health: Record<string, string>) => void
}

export const useWorkspaceStore = create<WorkspaceStore>((set) => ({
  activeRightPanel: 'config',
  selectedNodeId: null,
  pipelineStatus: 'idle',
  nifiStatus: 'unknown',
  lastQueryInfo: null,
  serviceHealth: {},
  setActiveRightPanel: (panel) => set({ activeRightPanel: panel }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setPipelineStatus: (status) => set({ pipelineStatus: status }),
  setNifiStatus: (status) => set({ nifiStatus: status }),
  setLastQueryInfo: (info) => set({ lastQueryInfo: info }),
  setServiceHealth: (serviceHealth) => set({ serviceHealth }),
}))
