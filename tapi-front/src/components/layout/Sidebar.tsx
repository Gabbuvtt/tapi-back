'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { clsx } from 'clsx';
import { 
  LayoutDashboard, 
  Award, 
  MessageSquare, 
  MenuSquare, 
  Nfc, 
  BellRing,
  Settings,
  LogOut,
  Coffee
} from 'lucide-react';
import styles from './Sidebar.module.css';
import { supabase } from '@/lib/supabase';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Programa de Lealtad', href: '/loyalty', icon: Award },
  { name: 'Reseñas', href: '/reviews', icon: MessageSquare },
  { name: 'Menú Digital', href: '/menu', icon: MenuSquare },
  { name: 'Etiquetas NFC', href: '/nfc', icon: Nfc },
  { name: 'Notificaciones', href: '/notifications', icon: BellRing },
];

export function Sidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/login');
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />
      )}
      
      <aside className={clsx(styles.sidebar, { [styles.sidebarOpen]: isOpen })}>
        <div className={styles.header}>
          <div className={styles.logoFull}>
            <img src="/tapi-logo-corto.png" alt="TAPI Isotipo" className={styles.logoImage} />
          </div>
          <button 
            className="lg:hidden" 
            onClick={onClose}
            style={{ position: 'absolute', right: '20px', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.6)', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
        
        <nav className={styles.nav}>
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(styles.navItem, { [styles.navItemActive]: isActive })}
                onClick={() => onClose()}
              >
                <item.icon className={styles.icon} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className={styles.footer} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <Link href="/settings" onClick={onClose} className={styles.settingsBtn} style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-text-secondary)', textDecoration: 'none', fontSize: '14px', transition: 'color 0.2s', padding: '8px', borderRadius: '8px' }}>
            <Settings size={18} />
            <span>Ajustes</span>
          </Link>
          <button 
            onClick={handleLogout} 
            title="Cerrar sesión"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,0,0,0.1)', color: '#ff4d4f', border: 'none', padding: '8px', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s' }}
            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,0,0,0.2)'}
            onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,0,0,0.1)'}
          >
            <LogOut size={18} />
          </button>
        </div>
      </aside>
    </>
  );
}
