import React from 'react';
import styles from './layout.module.css';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.container}>
      {/* Left Pane (Branding) */}
      <div className={styles.leftPane}>
        <div className={styles.brand}>
          <img src="/tapi-completo.png" alt="TAPI Logo" style={{ width: '280px', height: 'auto', marginBottom: '1rem', objectFit: 'contain' }} />
          <div className={styles.tagline}>
            Sistema de Fidelización NFC para tu Negocio
          </div>
        </div>
        
        <div className={styles.illustration}>
          {/* Decorative shapes to match design system */}
          <svg width="320" height="320" viewBox="0 0 320 320" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="160" cy="160" r="160" fill="var(--color-primary-light)" fillOpacity="0.2"/>
            <circle cx="160" cy="160" r="120" fill="var(--color-primary-light)" fillOpacity="0.4"/>
            <rect x="100" y="80" width="120" height="160" rx="16" fill="var(--color-secondary)" />
            <rect x="120" y="100" width="80" height="20" rx="8" fill="var(--color-on-secondary)" fillOpacity="0.8"/>
            <rect x="120" y="140" width="50" height="10" rx="4" fill="var(--color-on-secondary)" fillOpacity="0.4"/>
          </svg>
        </div>
      </div>

      {/* Right Pane (Form) */}
      <div className={styles.rightPane}>
        {children}
      </div>
    </div>
  );
}
