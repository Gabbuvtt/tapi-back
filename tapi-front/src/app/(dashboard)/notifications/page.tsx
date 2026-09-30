'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, Mail, MessageSquare, Send } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './notifications.module.css';

export default function NotificationsPage() {
  const [storeId, setStoreId] = useState<string | null>(null);
  const [campaignsState, setCampaignsState] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCampaign, setNewCampaign] = useState({ name: '', type: 'Push', message: '' });

  useEffect(() => {
    async function loadCampaigns() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        setStoreId(store.id);
        const { data: notifs } = await supabase
          .from('notifications')
          .select('*')
          .eq('store_id', store.id)
          .order('created_at', { ascending: false });
          
        if (notifs) {
          setCampaignsState(notifs);
        }
      }
      setIsLoading(false);
    }
    loadCampaigns();
  }, []);

  const handleSave = async () => {
    if (!newCampaign.name.trim() || !storeId) return;
    setIsSaving(true);
    
    try {
      const { data } = await supabase.from('notifications').insert({
        store_id: storeId,
        title: newCampaign.name,
        message: newCampaign.message || 'Mensaje de campaña',
        type: newCampaign.type
      }).select().single();
      
      if (data) {
        setCampaignsState([data, ...campaignsState]);
        setIsModalOpen(false);
      }
    } catch (e) {
      console.error(e);
      alert('Error al guardar la campaña');
    }
    setIsSaving(false);
  };

  if (isLoading) return <div>Cargando Campañas...</div>;

  return (
    <>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Campañas</h1>
          <p className={styles.subtitle}>Comunícate con tus clientes y aumenta tus ventas</p>
        </div>
        <Button 
          leftIcon={<Plus size={18} />} 
          variant="secondary"
          onClick={() => {
            setNewCampaign({ name: '', type: 'Push', message: '' });
            setIsModalOpen(true);
          }}
        >
          Nueva Campaña
        </Button>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={`${styles.iconWrapper} ${styles.iconPrimary}`}>
            <Send size={20} />
          </div>
          <div className={styles.statInfo}>
            <div className={styles.statValue}>{campaignsState.length * 5}</div>
            <div className={styles.statLabel}>Mensajes Enviados</div>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={`${styles.iconWrapper} ${styles.iconSuccess}`}>
            <MessageSquare size={20} />
          </div>
          <div className={styles.statInfo}>
            <div className={styles.statValue}>32%</div>
            <div className={styles.statLabel}>Tasa de Apertura Push</div>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={`${styles.iconWrapper} ${styles.iconSecondary}`}>
            <Mail size={20} />
          </div>
          <div className={styles.statInfo}>
            <div className={styles.statValue}>18%</div>
            <div className={styles.statLabel}>Tasa de Apertura Email</div>
          </div>
        </div>
      </div>

      <div className={styles.tableSection}>
        <h2 className={styles.sectionTitle}>Historial de Campañas</h2>
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Nombre de Campaña</th>
                <th>Tipo</th>
                <th>Enviados</th>
                <th>Aperturas</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {campaignsState.length > 0 ? campaignsState.map(camp => (
                <tr key={camp.id}>
                  <td>
                    <span className={styles.campaignName}>{camp.title}</span>
                  </td>
                  <td>
                    <span className={`${styles.badge} ${camp.type === 'Push' ? styles.badgePush : styles.badgeEmail}`}>
                      {camp.type}
                    </span>
                  </td>
                  <td style={{ color: 'var(--color-text-secondary)' }}>-</td>
                  <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>-</td>
                  <td style={{ color: 'var(--color-text-muted)' }}>{new Date(camp.created_at).toLocaleDateString()}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="text-center py-4 text-gray-500">No tienes campañas creadas.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>Nueva Campaña</h2>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Nombre de la Campaña</label>
              <input 
                type="text" 
                className={styles.input} 
                value={newCampaign.name}
                onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
                placeholder="Ej. Descuento 20% Cumpleaños" 
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Mensaje</label>
              <input 
                type="text" 
                className={styles.input} 
                value={newCampaign.message}
                onChange={(e) => setNewCampaign({...newCampaign, message: e.target.value})}
                placeholder="¡Ven a celebrar tu cumple con nosotros!" 
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Tipo de Envío</label>
              <select 
                className={styles.input}
                value={newCampaign.type}
                onChange={(e) => setNewCampaign({...newCampaign, type: e.target.value})}
              >
                <option value="Push">Notificación Push</option>
                <option value="Email">Email Marketing</option>
              </select>
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSave} isLoading={isSaving} disabled={!newCampaign.name.trim()}>
                Guardar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
