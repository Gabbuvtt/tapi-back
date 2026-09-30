'use client';

import React, { useEffect, useState } from 'react';
import { Menu, Search, ChevronDown } from 'lucide-react';
import styles from './Topbar.module.css';
import { useAuthStore } from '@/lib/stores/authStore';
import { supabase } from '@/lib/supabase';

export function Topbar({ onMenuClick, storeName = 'TAPI', storeId }: { onMenuClick: () => void, storeName?: string, storeId?: string }) {
  const user = useAuthStore(state => state.user);
  const [nfcCount, setNfcCount] = useState(0);

  useEffect(() => {
    async function loadNFCs() {
      if (!storeId) return;
      const { count } = await supabase
        .from('nfc_tags')
        .select('*', { count: 'exact', head: true })
        .eq('store_id', storeId)
        .eq('status', 'active');
      setNfcCount(count || 0);
    }
    loadNFCs();
  }, [storeId]);

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
            {storeName} <ChevronDown size={14} className="text-gray-400" />
          </div>
          <div className={styles.systemStatus}>
            <span className={styles.pulseDot} style={{ background: nfcCount > 0 ? '#10B981' : '#6B7280' }}></span>
            {nfcCount} NFC Beacons Activos
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
