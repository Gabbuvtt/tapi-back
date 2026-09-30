'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { Topbar } from '@/components/layout/Topbar';
import { supabase } from '@/lib/supabase';
import styles from './layout.module.css';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userStore, setUserStore] = useState<any>(null);
  const router = useRouter();

  // Validación real de Supabase y acceso a la tienda
  useEffect(() => {
    async function checkAuthAndStore() {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.user || !session.user.email) {
        router.push('/login');
        return;
      }

      // Validar si el correo de este usuario es dueño de alguna tienda
      let { data: store } = await supabase
        .from('stores')
        .select('*')
        .eq('owner_email', session.user.email)
        .single();

      // TODO: Para la Versión 2.0 (SaaS Abierto), aquí podríamos auto-crear la tienda 
      // y mandarlos a pagar con Stripe. Por ahora, en Fase 1, es un sistema CERRADO B2B.
      // El administrador (TAPI) debe crear la tienda manualmente en Supabase.
      /*
      if (!store) {
        const slugBase = session.user.email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, '-');
        const { data: newStore } = await supabase.from('stores').insert({
          name: 'Mi Nueva Tienda',
          slug: slugBase + '-' + Math.floor(Math.random() * 1000),
          owner_email: session.user.email,
          owner_id: session.user.id,
          is_onboarded: false
        }).select().single();
        
        store = newStore;
      }
      */

      if (store) {
        setUserStore(store);
        if (!store.is_onboarded && window.location.pathname !== '/onboarding') {
          router.push('/onboarding');
        }
      }
      setIsLoading(false);
    }
    
    checkAuthAndStore();
  }, [router]);

  if (isLoading) {
    return (
      <div className={styles.layout} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0b1521', color: 'white' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--color-secondary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p>Verificando permisos...</p>
        </div>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  // Si no tiene tienda autorizada
  if (!userStore) {
    return (
      <div className={styles.layout} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0b1521' }}>
        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '40px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)', textAlign: 'center', maxWidth: '400px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔒</div>
          <h2 style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>Acceso Restringido</h2>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '32px', lineHeight: 1.5 }}>
            Tu correo electrónico no tiene permisos para acceder a ningún panel de administración de TAPI.
          </p>
          <button 
            onClick={() => supabase.auth.signOut().then(() => router.push('/login'))} 
            style={{ width: '100%', padding: '14px', background: 'var(--color-secondary)', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    );
  }

  // Si no ha hecho onboarding, solo mostramos el Wizard limpio sin menú lateral
  if (!userStore.is_onboarded) {
    return (
      <div className={styles.layout}>
        <main className={styles.content} style={{ padding: 0 }}>
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className={styles.layout}>
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />
      
      <div className={styles.mainWrapper}>
        <Topbar onMenuClick={() => setIsSidebarOpen(true)} storeName={userStore.name} storeId={userStore.id} />
        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  );
}
