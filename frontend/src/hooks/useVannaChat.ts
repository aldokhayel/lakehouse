// useVannaChat.ts — Vanna AI chat hook: ask (generate SQL) and execute (run SQL via Trino).
'use client'
import { useState } from 'react'
import { chatApi } from '@/lib/api'
import { useChatStore } from '@/stores/chatStore'
import type { ChatMessage } from '@/types/chat'

function newId() {
  return Math.random().toString(36).slice(2)
}

export function useVannaChat() {
  const { addMessage, updateMessage, setLoading, isLoading } = useChatStore()
  const [input, setInput] = useState('')

  async function ask(question: string) {
    if (!question.trim()) return
    setInput('')
    setLoading(true)

    const userId = newId()
    const assistantId = newId()

    addMessage({ id: userId, role: 'user', content: question, status: 'success', timestamp: Date.now() })
    addMessage({ id: assistantId, role: 'assistant', content: '', status: 'generating', timestamp: Date.now() })

    try {
      const res = await chatApi.ask(question)
      const sql: string | undefined = res.data?.generated_sql
      const messageId: string | undefined = res.data?.message_id

      if (!sql) throw new Error(res.data?.error ?? 'No SQL generated')

      updateMessage(assistantId, {
        status: 'ready',
        sql,
        editedSql: sql,
        content: sql,
        id: assistantId,
      })
      // Store backend messageId via a custom field on the message object
      useChatStore.getState().updateMessage(assistantId, { ...(messageId ? { _backendId: messageId } as any : {}) })
    } catch (err: any) {
      updateMessage(assistantId, { status: 'error', error: err.message })
    } finally {
      setLoading(false)
    }
  }

  async function execute(assistantId: string, sql: string) {
    const msg = useChatStore.getState().messages.find((m) => m.id === assistantId)
    const backendId = (msg as any)?._backendId

    updateMessage(assistantId, { status: 'executing', editedSql: sql })

    try {
      const res = await chatApi.execute(sql, backendId)
      const d = res.data
      if (!d || d.error) throw new Error(d?.error ?? 'Execution failed')

      updateMessage(assistantId, {
        status: 'success',
        chartType: 'table',
        results: {
          columns: d.columns,
          rows: d.rows,
          rowCount: d.row_count,
          executionTimeMs: d.execution_time_ms,
        },
      })
    } catch (err: any) {
      updateMessage(assistantId, { status: 'error', error: err.message })
    }
  }

  return { input, setInput, ask, execute, isLoading }
}
