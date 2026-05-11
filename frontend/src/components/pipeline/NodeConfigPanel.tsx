// NodeConfigPanel.tsx — Right panel Config tab: renders context-sensitive forms for the selected pipeline node.
'use client'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { usePipelineStore } from '@/stores/pipelineStore'

function Field({ label, value, onChange, type = 'text', placeholder = '' }: {
  label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string
}) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', color: '#64748b', fontSize: 11, fontWeight: 700, letterSpacing: '0.06em', marginBottom: 4 }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%', background: '#0f1117', border: '1px solid #2d3142',
          borderRadius: 6, padding: '7px 10px', color: '#e2e8f0',
          fontSize: 13, outline: 'none', boxSizing: 'border-box',
        }}
      />
    </div>
  )
}

function Select({ label, value, onChange, options }: {
  label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[]
}) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', color: '#64748b', fontSize: 11, fontWeight: 700, letterSpacing: '0.06em', marginBottom: 4 }}>
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%', background: '#0f1117', border: '1px solid #2d3142',
          borderRadius: 6, padding: '7px 10px', color: '#e2e8f0',
          fontSize: 13, outline: 'none',
        }}
      >
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}

function ApiSourceForm({ config, update }: { config: Record<string, string>; update: (k: string, v: string) => void }) {
  return (
    <>
      <Field label="URL" value={config.url ?? ''} onChange={(v) => update('url', v)} placeholder="https://api.example.com/data" />
      <Select label="METHOD" value={config.method ?? 'GET'} onChange={(v) => update('method', v)} options={[{ value: 'GET', label: 'GET' }, { value: 'POST', label: 'POST' }]} />
      <Field label="SCHEDULE" value={config.schedule ?? '1 hour'} onChange={(v) => update('schedule', v)} placeholder="1 hour" />
      <Select label="AUTH TYPE" value={config.authType ?? 'none'} onChange={(v) => update('authType', v)} options={[{ value: 'none', label: 'None' }, { value: 'bearer', label: 'Bearer Token' }, { value: 'basic', label: 'Basic' }]} />
      {config.authType !== 'none' && (
        <Field label="AUTH VALUE" value={config.authValue ?? ''} onChange={(v) => update('authValue', v)} placeholder="Token or user:password" />
      )}
      <Field label="HEADERS (JSON)" value={config.headers ?? '{}'} onChange={(v) => update('headers', v)} placeholder='{"Accept": "application/json"}' />
    </>
  )
}

function DbSourceForm({ config, update, dbType }: { config: Record<string, string>; update: (k: string, v: string) => void; dbType: string }) {
  return (
    <>
      <Field label="HOST" value={config.host ?? ''} onChange={(v) => update('host', v)} placeholder="db-server.local" />
      <Field label="PORT" value={config.port ?? (dbType === 'mssql' ? '1433' : '5432')} onChange={(v) => update('port', v)} />
      <Field label="DATABASE" value={config.database ?? ''} onChange={(v) => update('database', v)} />
      <Field label="USERNAME" value={config.username ?? ''} onChange={(v) => update('username', v)} />
      <Field label="PASSWORD" value={config.password ?? ''} onChange={(v) => update('password', v)} type="password" />
      <Field label="QUERY / TABLE" value={config.query ?? ''} onChange={(v) => update('query', v)} placeholder="SELECT * FROM orders" />
    </>
  )
}

function MongoForm({ config, update }: { config: Record<string, string>; update: (k: string, v: string) => void }) {
  return (
    <>
      <Field label="URI" value={config.uri ?? ''} onChange={(v) => update('uri', v)} placeholder="mongodb://user:pass@host:27017" />
      <Field label="DATABASE" value={config.database ?? ''} onChange={(v) => update('database', v)} />
      <Field label="COLLECTION" value={config.collection ?? ''} onChange={(v) => update('collection', v)} />
      <Field label="FILTER (JSON)" value={config.filter ?? '{}'} onChange={(v) => update('filter', v)} placeholder="{}" />
    </>
  )
}

function TransformForm({ config, update }: { config: Record<string, string>; update: (k: string, v: string) => void }) {
  return (
    <>
      <Field label="DBT MODEL NAME" value={config.modelName ?? ''} onChange={(v) => update('modelName', v)} placeholder="stg_orders" />
    </>
  )
}

function DestinationForm({ config, update }: { config: Record<string, string>; update: (k: string, v: string) => void }) {
  return (
    <>
      <Select label="LAYER" value={config.schema ?? 'raw'} onChange={(v) => update('schema', v)} options={[{ value: 'raw', label: 'Raw' }, { value: 'staging', label: 'Staging' }, { value: 'mart', label: 'Mart' }]} />
      <Field label="TABLE NAME" value={config.tableName ?? ''} onChange={(v) => update('tableName', v)} placeholder="raw_orders" />
    </>
  )
}

function NiFiFlowForm({ config, update }: { config: Record<string, string>; update: (k: string, v: string) => void }) {
  return (
    <>
      <Field label="NIFI FLOW ID" value={config.flowId ?? ''} onChange={(v) => update('flowId', v)} placeholder="UUID of NiFi process group" />
      <Select label="TEMPLATE" value={config.templateName ?? 'api-to-minio'} onChange={(v) => update('templateName', v)} options={[
        { value: 'api-to-minio', label: 'API → MinIO' },
        { value: 'postgres-to-minio', label: 'PostgreSQL → MinIO' },
        { value: 'mssql-to-minio', label: 'MSSQL → MinIO' },
        { value: 'mongodb-to-minio', label: 'MongoDB → MinIO' },
      ]} />
    </>
  )
}

export function NodeConfigPanel() {
  const selectedNodeId = useWorkspaceStore((s) => s.selectedNodeId)
  const { nodes, nodeConfigs, updateNodeConfig } = usePipelineStore()

  if (!selectedNodeId) {
    return (
      <div style={{ padding: 24, color: '#64748b', fontSize: 13, lineHeight: 1.6 }}>
        <div style={{ fontSize: 24, marginBottom: 12 }}>🎯</div>
        <div style={{ fontWeight: 600, color: '#94a3b8', marginBottom: 8 }}>No node selected</div>
        <div>Click a node on the canvas to configure it, or drag a new node from the palette.</div>
      </div>
    )
  }

  const node = nodes.find((n) => n.id === selectedNodeId)
  if (!node) return null

  const config = nodeConfigs[selectedNodeId] ?? {}
  const update = (key: string, value: string) => {
    updateNodeConfig(selectedNodeId, { ...config, [key]: value })
  }

  const nodeType = node.type
  const sourceType = (node.data.sourceType as string) ?? ''

  return (
    <div style={{ padding: '16px 16px', overflowY: 'auto', flex: 1 }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ color: '#94a3b8', fontSize: 12, fontWeight: 700, letterSpacing: '0.08em' }}>
          NODE CONFIG
        </div>
        <div style={{ color: '#e2e8f0', fontSize: 15, fontWeight: 600, marginTop: 4 }}>
          {(node.data.label as string) || node.type}
        </div>
      </div>

      {nodeType === 'source' && sourceType === 'api' && <ApiSourceForm config={config} update={update} />}
      {nodeType === 'source' && sourceType === 'mssql' && <DbSourceForm config={config} update={update} dbType="mssql" />}
      {nodeType === 'source' && sourceType === 'postgresql' && <DbSourceForm config={config} update={update} dbType="postgresql" />}
      {nodeType === 'source' && sourceType === 'mongodb' && <MongoForm config={config} update={update} />}
      {nodeType === 'transform' && <TransformForm config={config} update={update} />}
      {nodeType === 'destination' && <DestinationForm config={config} update={update} />}
      {nodeType === 'nifi_flow' && <NiFiFlowForm config={config} update={update} />}
    </div>
  )
}
