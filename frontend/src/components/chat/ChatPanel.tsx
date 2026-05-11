// ChatPanel.tsx — Vanna AI natural-language SQL chat interface with results table and charts.
'use client'
import { useRef, useEffect, useState } from 'react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { useChatStore } from '@/stores/chatStore'
import { useVannaChat } from '@/hooks/useVannaChat'
import type { ChatMessage, ChartType, QueryResults } from '@/types/chat'

const COLORS = ['#3b82f6', '#10b981', '#f97316', '#a855f7', '#ef4444', '#06b6d4', '#eab308']

// ---------------------------------------------------------------------------
// SQL code block with inline editing and run button
// ---------------------------------------------------------------------------
function SqlBlock({ msg, onExecute }: { msg: ChatMessage; onExecute: (id: string, sql: string) => void }) {
  const [editing, setEditing] = useState(false)
  const [sql, setSql] = useState(msg.editedSql ?? msg.sql ?? '')
  const running = msg.status === 'executing'

  return (
    <div style={{ marginTop: 8 }}>
      <div style={{
        background: '#0d1117', border: '1px solid #2d3142', borderRadius: 6,
        padding: '10px 12px', fontFamily: 'monospace', fontSize: 12,
        color: '#c9d1d9', position: 'relative',
      }}>
        {editing ? (
          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            style={{
              width: '100%', background: 'transparent', border: 'none', outline: 'none',
              color: '#c9d1d9', fontFamily: 'monospace', fontSize: 12,
              resize: 'vertical', minHeight: 60,
            }}
          />
        ) : (
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{sql}</pre>
        )}
      </div>
      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
        <button
          onClick={() => setEditing((e) => !e)}
          style={{
            background: '#2d3142', border: 'none', borderRadius: 5, color: '#94a3b8',
            padding: '4px 10px', fontSize: 12, cursor: 'pointer',
          }}
        >
          {editing ? 'Done' : 'Edit SQL'}
        </button>
        <button
          onClick={() => { setEditing(false); onExecute(msg.id, sql) }}
          disabled={running}
          style={{
            background: running ? '#1e3a2a' : '#10b981', border: 'none', borderRadius: 5,
            color: 'white', padding: '4px 12px', fontSize: 12,
            cursor: running ? 'not-allowed' : 'pointer', fontWeight: 600,
          }}
        >
          {running ? 'Running…' : '▶ Run SQL'}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Chart type toggle
// ---------------------------------------------------------------------------
function ChartToggle({ current, onChange }: { current: ChartType; onChange: (t: ChartType) => void }) {
  const types: ChartType[] = ['table', 'bar', 'line', 'pie']
  const labels: Record<ChartType, string> = { table: 'Table', bar: 'Bar', line: 'Line', pie: 'Pie' }
  return (
    <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
      {types.map((t) => (
        <button
          key={t}
          onClick={() => onChange(t)}
          style={{
            padding: '3px 10px', fontSize: 11, borderRadius: 4, cursor: 'pointer', border: 'none',
            background: current === t ? '#3b82f6' : '#2d3142',
            color: current === t ? 'white' : '#94a3b8',
            fontWeight: current === t ? 600 : 400,
          }}
        >
          {labels[t]}
        </button>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Results table
// ---------------------------------------------------------------------------
function ResultsTable({ results }: { results: QueryResults }) {
  const { columns, rows } = results
  return (
    <div style={{ overflowX: 'auto', maxHeight: 260, overflowY: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col} style={{
                padding: '6px 10px', background: '#1a1d27', color: '#94a3b8',
                fontWeight: 600, textAlign: 'left', borderBottom: '1px solid #2d3142',
                position: 'sticky', top: 0, whiteSpace: 'nowrap',
              }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? 'transparent' : '#ffffff05' }}>
              {row.map((cell, j) => (
                <td key={j} style={{
                  padding: '5px 10px', color: '#e2e8f0',
                  borderBottom: '1px solid #2d314240', whiteSpace: 'nowrap',
                }}>
                  {cell === null ? <span style={{ color: '#64748b' }}>NULL</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Recharts wrapper — picks bar/line/pie based on chartType
// ---------------------------------------------------------------------------
function ResultsChart({ results, chartType }: { results: QueryResults; chartType: ChartType }) {
  const { columns, rows } = results
  if (columns.length < 2) return <p style={{ color: '#64748b', fontSize: 12 }}>Need at least 2 columns for a chart.</p>

  const data = rows.map((row) => {
    const obj: Record<string, any> = {}
    columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
  const xKey = columns[0]
  const yKeys = columns.slice(1)

  const commonProps = { data, margin: { top: 4, right: 8, left: 0, bottom: 4 } }

  if (chartType === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={220}>
        <BarChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3142" />
          <XAxis dataKey={xKey} tick={{ fill: '#64748b', fontSize: 11 }} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
          <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3142', color: '#e2e8f0', fontSize: 12 }} />
          {yKeys.map((k, i) => <Bar key={k} dataKey={k} fill={COLORS[i % COLORS.length]} radius={[3, 3, 0, 0]} />)}
        </BarChart>
      </ResponsiveContainer>
    )
  }
  if (chartType === 'line') {
    return (
      <ResponsiveContainer width="100%" height={220}>
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3142" />
          <XAxis dataKey={xKey} tick={{ fill: '#64748b', fontSize: 11 }} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
          <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3142', color: '#e2e8f0', fontSize: 12 }} />
          {yKeys.map((k, i) => <Line key={k} dataKey={k} stroke={COLORS[i % COLORS.length]} dot={false} strokeWidth={2} />)}
        </LineChart>
      </ResponsiveContainer>
    )
  }
  if (chartType === 'pie') {
    const pieData = rows.map((row) => ({ name: String(row[0]), value: Number(row[1]) }))
    return (
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
            {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3142', color: '#e2e8f0', fontSize: 12 }} />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 11 }} />
        </PieChart>
      </ResponsiveContainer>
    )
  }
  return null
}

// ---------------------------------------------------------------------------
// Results block: toggle + table/chart
// ---------------------------------------------------------------------------
function ResultsBlock({ msg }: { msg: ChatMessage }) {
  const { updateMessage } = useChatStore()
  const chartType = msg.chartType ?? 'table'
  if (!msg.results) return null

  return (
    <div style={{ marginTop: 10 }}>
      <ChartToggle current={chartType} onChange={(t) => updateMessage(msg.id, { chartType: t })} />
      {chartType === 'table'
        ? <ResultsTable results={msg.results} />
        : <ResultsChart results={msg.results} chartType={chartType} />}
      <div style={{ marginTop: 4, color: '#64748b', fontSize: 11 }}>
        {msg.results.rowCount} rows
        {msg.results.executionTimeMs !== undefined && ` · ${msg.results.executionTimeMs.toFixed(0)}ms`}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Individual message bubble
// ---------------------------------------------------------------------------
function MessageBubble({ msg, onExecute }: { msg: ChatMessage; onExecute: (id: string, sql: string) => void }) {
  const isUser = msg.role === 'user'

  if (isUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
        <div style={{
          background: '#1e3a5f', color: '#e2e8f0', borderRadius: '12px 12px 2px 12px',
          padding: '8px 14px', fontSize: 13, maxWidth: '80%', wordBreak: 'break-word',
        }}>
          {msg.content}
        </div>
      </div>
    )
  }

  // Assistant bubble
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
        <div style={{
          width: 28, height: 28, borderRadius: '50%', background: '#1a1d27',
          border: '1px solid #2d3142', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, flexShrink: 0, marginTop: 2,
        }}>
          🤖
        </div>
        <div style={{ flex: 1 }}>
          {msg.status === 'generating' && (
            <div style={{ color: '#64748b', fontSize: 13 }}>Generating SQL…</div>
          )}
          {msg.status === 'error' && (
            <div style={{
              background: '#2d1515', border: '1px solid #ef4444', borderRadius: 6,
              padding: '8px 12px', color: '#fca5a5', fontSize: 13,
            }}>
              {msg.error}
            </div>
          )}
          {(msg.status === 'ready' || msg.status === 'executing' || msg.status === 'success') && msg.sql && (
            <>
              <div style={{ color: '#94a3b8', fontSize: 12, marginBottom: 4 }}>Generated SQL:</div>
              <SqlBlock msg={msg} onExecute={onExecute} />
            </>
          )}
          {msg.status === 'success' && msg.results && <ResultsBlock msg={msg} />}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Auto-train banner
// ---------------------------------------------------------------------------
function AutoTrainBanner() {
  const [state, setState] = useState<'idle' | 'loading' | 'done' | 'error'>('idle')

  async function handleAutoTrain() {
    setState('loading')
    try {
      const { chatApi } = await import('@/lib/api')
      await chatApi.autoTrain()
      setState('done')
    } catch {
      setState('error')
    }
  }

  return (
    <div style={{
      background: '#1a1d27', border: '1px solid #2d3142', borderRadius: 8,
      padding: '10px 14px', marginBottom: 12, fontSize: 12, color: '#94a3b8',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
    }}>
      <span>
        {state === 'done' ? '✅ Schema trained!' : state === 'error' ? '❌ Training failed' : '📚 Train Vanna on your Trino schema to improve SQL generation.'}
      </span>
      {(state === 'idle' || state === 'error') && (
        <button
          onClick={handleAutoTrain}
          style={{
            background: '#2d3142', border: 'none', borderRadius: 5, color: '#e2e8f0',
            padding: '4px 10px', fontSize: 11, cursor: 'pointer', whiteSpace: 'nowrap',
          }}
        >
          Auto-train
        </button>
      )}
      {state === 'loading' && <span style={{ color: '#64748b' }}>Training…</span>}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main ChatPanel export
// ---------------------------------------------------------------------------
export function ChatPanel() {
  const { messages } = useChatStore()
  const { input, setInput, ask, execute, isLoading } = useVannaChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask(input)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Messages area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 14px 0' }}>
        <AutoTrainBanner />
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: '#64748b' }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>💬</div>
            <div style={{ fontWeight: 600, color: '#94a3b8', marginBottom: 6 }}>Ask anything about your data</div>
            <div style={{ fontSize: 12, lineHeight: 1.7 }}>
              &quot;Show total revenue by month&quot;<br />
              &quot;Top 10 customers by order count&quot;<br />
              &quot;Average order value in the last 90 days&quot;
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} onExecute={execute} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div style={{
        borderTop: '1px solid #2d3142', padding: '12px 14px',
        display: 'flex', gap: 8, alignItems: 'flex-end', flexShrink: 0,
      }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your data… (Enter to send)"
          rows={2}
          style={{
            flex: 1, background: '#1a1d27', border: '1px solid #2d3142', borderRadius: 8,
            color: '#e2e8f0', fontSize: 13, padding: '8px 12px', resize: 'none', outline: 'none',
            fontFamily: 'inherit',
          }}
        />
        <button
          onClick={() => ask(input)}
          disabled={isLoading || !input.trim()}
          style={{
            background: isLoading || !input.trim() ? '#2d3142' : '#3b82f6',
            border: 'none', borderRadius: 8, color: 'white',
            padding: '10px 16px', fontSize: 13, cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
            fontWeight: 600, flexShrink: 0, height: 42,
          }}
        >
          {isLoading ? '…' : 'Send'}
        </button>
      </div>
    </div>
  )
}
