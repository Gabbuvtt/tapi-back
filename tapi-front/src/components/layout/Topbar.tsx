'use client';

import React from 'react';
import { Menu, Search, ChevronDown } from 'lucide-react';
import styles from './Topbar.module.css';
import { useAuthStore } from '@/lib/stores/authStore';

export function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  const user = useAuthStore(state => state.user);

  const initials = user?.full_name 
    ? user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
    : 'TA';

  return (
    <header className={styles.topbar}>
      <div className={styles.left}>
        <button className={styles.menuButton} onClick={onMenuClick}>
          <Menu size={20} />
        </button>
        
        <div className={styles.contextSelector}>
          <div className={styles.locationName}>
            Café El Aroma <ChevronDown size={14} className="text-gray-400" />
          </div>
          <div className={styles.systemStatus}>
            <span className={styles.pulseDot}></span>
            12 NFC Beacons Activos
          </div>
        </div>
      </div>

      <div className={styles.right}>
        <div className={styles.search}>
          <Search size={16} />
          <span>Buscar...</span>
          <span className={styles.shortcut}>⌘K</span>
        </div>

        <div className={styles.profile}>
          <div className={styles.avatar}>
            {initials}
            <span className={styles.proBadge}>PRO</span>
          </div>
        </div>
      </div>
    </header>
  );
}
