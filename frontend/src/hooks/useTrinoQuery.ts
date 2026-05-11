// useTrinoQuery.ts — React Query mutation hook for executing Trino SQL queries and updating status bar.
'use client'
import { useMutation } from '@tanstack/react-query'
import { trinoApi } from '@/lib/api'
import { useWorkspaceStore } from '@/stores/workspaceStore'

export function useTrinoQuery() {
  const setLastQueryInfo = useWorkspaceStore((s) => s.setLastQueryInfo)
  return useMutation({
    mutationFn: ({ sql, catalog }: { sql: string; catalog?: string }) =>
      trinoApi.query(sql, catalog),
    onSuccess: (res) => {
      setLastQueryInfo(`${res.data?.row_count ?? 0} rows returned`)
    },
  })
}
