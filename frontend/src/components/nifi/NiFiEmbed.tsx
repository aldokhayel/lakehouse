// NiFiEmbed.tsx — Iframe wrapper for the Apache NiFi UI with self-signed certificate warning.
'use client'
import { NIFI_URL } from '@/lib/constants'

export function NiFiEmbed() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{
        padding: '8px 12px',
        background: '#1a1d27',
        borderBottom: '1px solid #2d3142',
        color: '#f59e0b',
        fontSize: 12,
      }}>
        ⚠️ NiFi uses a self-signed HTTPS cert. If the iframe is blank, open{' '}
        <a href={`${NIFI_URL}/nifi`} target="_blank" rel="noreferrer" style={{ color: '#3b82f6' }}>
          {NIFI_URL}/nifi
        </a>{' '}
        in a new tab and accept the certificate, then return here.
      </div>
      <iframe
        src={`${NIFI_URL}/nifi`}
        style={{ flex: 1, border: 'none', width: '100%' }}
        title="Apache NiFi"
        allow="same-origin"
      />
    </div>
  )
}
