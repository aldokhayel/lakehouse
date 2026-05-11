// chat.ts — TypeScript types for Vanna AI chat messages and query results.
export interface QueryResults {
  columns: string[]
  rows: (string | number | null)[][]
  rowCount: number
  executionTimeMs?: number
}

export type ChartType = 'table' | 'bar' | 'line' | 'pie'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string
  editedSql?: string
  results?: QueryResults
  chartType?: ChartType
  status: 'pending' | 'generating' | 'ready' | 'executing' | 'success' | 'error'
  error?: string
  timestamp: number
}
