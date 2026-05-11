// datasource.ts — TypeScript type for data source records returned by the backend API.
export interface DataSource {
  id: string
  name: string
  type: 'api' | 'mssql' | 'postgresql' | 'mongodb'
  config: Record<string, string>
  is_active: boolean
  created_at: string
}
