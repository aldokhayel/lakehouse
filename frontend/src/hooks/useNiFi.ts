// useNiFi.ts — React Query hooks for NiFi status polling and flow start/stop mutations.
'use client'
import { useQuery, useMutation } from '@tanstack/react-query'
import { nifiApi } from '@/lib/api'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { useEffect } from 'react'

export function useNiFiStatus() {
  const setNifiStatus = useWorkspaceStore((s) => s.setNifiStatus)
  const query = useQuery({
    queryKey: ['nifi-status'],
    queryFn: nifiApi.status,
    refetchInterval: 30_000,
    retry: false,
  })
  useEffect(() => {
    if (query.isSuccess) setNifiStatus('healthy')
    if (query.isError) setNifiStatus('error')
  }, [query.isSuccess, query.isError, setNifiStatus])
  return query
}

export function useStartFlow(flowId: string) {
  return useMutation({ mutationFn: () => nifiApi.startFlow(flowId) })
}

export function useStopFlow(flowId: string) {
  return useMutation({ mutationFn: () => nifiApi.stopFlow(flowId) })
}
