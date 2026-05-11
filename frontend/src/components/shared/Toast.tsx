// Toast.tsx — Simple overlay toast notification component (wired up in Phase 5).
'use client'
export function Toast({ message, type = 'info' }: { message: string; type?: 'info' | 'success' | 'error' }) {
  const colors = { info: '#3b82f6', success: '#10b981', error: '#ef4444' }
  return (
    <div style={{
      position: 'fixed', bottom: 48, right: 16, zIndex: 9999,
      background: '#1a1d27', border: `1px solid ${colors[type]}`,
      borderRadius: 8, padding: '10px 16px',
      color: '#e2e8f0', fontSize: 13,
    }}>
      <span style={{ color: colors[type] }}>●</span> {message}
    </div>
  )
}
