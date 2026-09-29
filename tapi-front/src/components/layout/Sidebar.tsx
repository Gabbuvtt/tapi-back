'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
import { useAuthStore } from '@/lib/stores/authStore';

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
  const logout = useAuthStore(state => state.logout);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}
      
      <aside className={clsx(styles.sidebar, { [styles.sidebarOpen]: isOpen })}>
        <div className={styles.header}>
          <div className={styles.logoFull}>
            <img src="/tapi-logo-corto.png" alt="TAPI Isotipo" className={styles.logoImage} />
          </div>
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

        <div className={styles.footer}>
          <Link href="/settings" className={styles.settingsBtn}>
            <Settings className={styles.icon} style={{ marginRight: '8px' }} />
            Ajustes
          </Link>
          <button onClick={logout} className="p-2 text-white/50 hover:text-[#E88B2E] transition-colors" title="Cerrar sesión">
            <LogOut size={18} />
          </button>
        </div>
      </aside>
    </>
  );
}
