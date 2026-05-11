// constants.ts — Application-wide constants: API URLs, node palette definitions, and defaults.
export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

export const NIFI_URL =
  process.env.NEXT_PUBLIC_NIFI_URL ?? 'https://localhost:8443'

export const GRAFANA_URL =
  process.env.NEXT_PUBLIC_GRAFANA_URL ?? 'http://localhost:3002'

export const NODE_PALETTE_ITEMS = [
  { label: 'API Source',        type: 'source',      sourceType: 'api',        icon: '🔌', color: '#3b82f6' },
  { label: 'MSSQL Source',      type: 'source',      sourceType: 'mssql',      icon: '🗄️', color: '#f97316' },
  { label: 'PostgreSQL Source', type: 'source',      sourceType: 'postgresql', icon: '🐘', color: '#06b6d4' },
  { label: 'MongoDB Source',    type: 'source',      sourceType: 'mongodb',    icon: '🍃', color: '#22c55e' },
  { label: 'NiFi Flow',         type: 'nifi_flow',   sourceType: null,         icon: '🌊', color: '#0ea5e9' },
  { label: 'dbt Model',         type: 'transform',   sourceType: null,         icon: '⚙️', color: '#a855f7' },
  { label: 'Iceberg Table',     type: 'destination', sourceType: null,         icon: '🏔️', color: '#10b981' },
] as const

export const DEFAULT_PIPELINE_NAME = 'Untitled Pipeline'
