// usePipeline.ts — React Query hooks for saving, running, and listing pipelines via the backend API.
'use client'
import { useMutation, useQuery } from '@tanstack/react-query'
import { pipelineApi } from '@/lib/api'
import { usePipelineStore } from '@/stores/pipelineStore'
import { useWorkspaceStore } from '@/stores/workspaceStore'

export function useSavePipeline() {
  const { nodes, edges, pipelineId, pipelineName, nodeConfigs, setPipelineId, markClean } = usePipelineStore()
  const { setPipelineStatus } = useWorkspaceStore()

  return useMutation({
    mutationFn: async () => {
      const definition = { nodes, edges, nodeConfigs }
      if (pipelineId) {
        return pipelineApi.update(pipelineId, { name: pipelineName, definition })
      }
      return pipelineApi.create({ name: pipelineName, description: '', definition })
    },
    onSuccess: (res) => {
      if (!pipelineId) setPipelineId(res.data?.id)
      markClean()
    },
    onError: () => setPipelineStatus('error'),
  })
}

export function useRunPipeline() {
  const { pipelineId } = usePipelineStore()
  const { setPipelineStatus } = useWorkspaceStore()

  return useMutation({
    mutationFn: () => {
      if (!pipelineId) throw new Error('Save the pipeline before running')
      return pipelineApi.run(pipelineId)
    },
    onMutate: () => setPipelineStatus('running'),
    onSuccess: () => setPipelineStatus('success'),
    onError: () => setPipelineStatus('error'),
  })
}

export function usePipelineList() {
  return useQuery({ queryKey: ['pipelines'], queryFn: () => pipelineApi.list() })
}
