// pipeline.ts — TypeScript types for pipeline nodes, edges, and configuration data.
export type NodeSourceType = 'api' | 'mssql' | 'postgresql' | 'mongodb'
export type NodeKind = 'source' | 'transform' | 'destination' | 'nifi_flow'

export interface ApiSourceConfig {
  url: string
  method: 'GET' | 'POST'
  headers: string         // JSON string of headers
  authType: 'none' | 'bearer' | 'basic'
  authValue: string
  schedule: string        // e.g. "1 hour"
}

export interface DbSourceConfig {
  host: string
  port: string
  database: string
  query: string
  username: string
  password: string
}

export interface MongoSourceConfig {
  uri: string
  database: string
  collection: string
  filter: string          // JSON filter
}

export interface TransformConfig {
  modelName: string
}

export interface DestinationConfig {
  schema: 'raw' | 'staging' | 'mart'
  tableName: string
}

export interface NiFiFlowConfig {
  flowId: string          // NiFi process group UUID
  templateName: string
}

export type NodeConfig =
  | { kind: 'api'; sourceType: 'api'; data: ApiSourceConfig }
  | { kind: 'source'; sourceType: Exclude<NodeSourceType, 'api'>; data: DbSourceConfig | MongoSourceConfig }
  | { kind: 'transform'; data: TransformConfig }
  | { kind: 'destination'; data: DestinationConfig }
  | { kind: 'nifi_flow'; data: NiFiFlowConfig }

export interface PipelineDefinition {
  nodes: unknown[]
  edges: unknown[]
  nifi_flow_id?: string
  dbt_select?: string
}
