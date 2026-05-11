// api.ts — All fetch calls to the FastAPI backend, organized by domain (pipeline, nifi, trino, dbt, chat).
import { BACKEND_URL } from './constants'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const json = await res.json()
  if (!res.ok || json.status === 'error') throw new Error(json.message ?? 'Request failed')
  return json
}

// Pipeline API
export const pipelineApi = {
  list:   ()                              => request<any>('/api/pipelines'),
  get:    (id: string)                   => request<any>(`/api/pipelines/${id}`),
  create: (body: object)                 => request<any>('/api/pipelines', { method: 'POST', body: JSON.stringify(body) }),
  update: (id: string, body: object)     => request<any>(`/api/pipelines/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (id: string)                   => request<any>(`/api/pipelines/${id}`, { method: 'DELETE' }),
  run:    (id: string)                   => request<any>(`/api/pipelines/${id}/run`, { method: 'POST' }),
  status: (id: string)                   => request<any>(`/api/pipelines/${id}/status`),
}

// NiFi API
export const nifiApi = {
  status:     ()                         => request<any>('/api/nifi/status'),
  listFlows:  ()                         => request<any>('/api/nifi/flows'),
  deploy:     (body: object)             => request<any>('/api/nifi/flows', { method: 'POST', body: JSON.stringify(body) }),
  startFlow:  (id: string)               => request<any>(`/api/nifi/flows/${id}/start`, { method: 'POST' }),
  stopFlow:   (id: string)               => request<any>(`/api/nifi/flows/${id}/stop`, { method: 'POST' }),
  flowStatus: (id: string)               => request<any>(`/api/nifi/flows/${id}/status`),
}

// Trino API
export const trinoApi = {
  query:    (sql: string, catalog?: string) => request<any>('/api/trino/query', { method: 'POST', body: JSON.stringify({ sql, catalog }) }),
  catalogs: ()                              => request<any>('/api/trino/catalogs'),
  schemas:  (catalog: string)              => request<any>(`/api/trino/schemas/${catalog}`),
  tables:   (catalog: string, schema: string) => request<any>(`/api/trino/tables/${catalog}/${schema}`),
}

// dbt API
export const dbtApi = {
  run:        (select?: string) => request<any>('/api/dbt/run', { method: 'POST', body: JSON.stringify({ select }) }),
  test:       (select?: string) => request<any>('/api/dbt/test', { method: 'POST', body: JSON.stringify({ select }) }),
  models:     ()                => request<any>('/api/dbt/models'),
  runResults: ()                => request<any>('/api/dbt/run-results'),
}

// Chat / Vanna AI API
export const chatApi = {
  ask:          (question: string)            => request<any>('/api/vanna/ask', { method: 'POST', body: JSON.stringify({ question }) }),
  execute:      (sql: string, messageId?: string) => request<any>('/api/vanna/execute', { method: 'POST', body: JSON.stringify({ sql, message_id: messageId }) }),
  history:      ()                            => request<any>('/api/vanna/history'),
  train:        (question: string, sql: string) => request<any>('/api/vanna/train', { method: 'POST', body: JSON.stringify({ question, sql }) }),
  autoTrain:    ()                            => request<any>('/api/vanna/auto-train', { method: 'POST' }),
  trainingData: ()                            => request<any>('/api/vanna/training-data'),
  status:       ()                            => request<any>('/api/vanna/status'),
}

// Health
export const healthApi = {
  check: () => request<any>('/api/health'),
}
