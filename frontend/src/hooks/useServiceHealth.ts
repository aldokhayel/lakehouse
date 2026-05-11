// useServiceHealth.ts — Polls /api/health every 30s and syncs results into workspaceStore.
'use client'
import { useEffect } from 'react'
import { healthApi } from '@/lib/api'
import { useWorkspaceStore } from '@/stores/workspaceStore'

export function useServiceHealth() {
  const setServiceHealth = useWorkspaceStore((s) => s.setServiceHealth)

  useEffect(() => {
    async function poll() {
      try {
        const res = await healthApi.check()
        setServiceHealth(res.data?.services ?? {})
      } catch {
        setServiceHealth({})
      }
    }

    poll()
    const id = setInterval(poll, 30_000)
    return () => clearInterval(id)
  }, [setServiceHealth])
}
