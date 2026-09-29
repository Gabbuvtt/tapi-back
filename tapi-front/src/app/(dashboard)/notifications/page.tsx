'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, Mail, MessageSquare, Send } from 'lucide-react';
import styles from './notifications.module.css';

export default function NotificationsPage() {
  const [campaignsState, setCampaignsState] = useState([
    { id: 1, name: 'Promo Fin de Semana', type: 'Push', sent: 1200, opened: 450, date: 'Ayer' },
    { id: 2, name: 'Reactivación de Usuarios', type: 'Email', sent: 800, opened: 210, date: 'Hace 3 días' },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCampaign, setNewCampaign] = useState({ name: '', type: 'Push' });

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
            setNewCampaign({ name: '', type: 'Push' });
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
            <div className={styles.statValue}>2,450</div>
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
            {campaignsState.map(camp => (
              <tr key={camp.id}>
                <td>
                  <span className={styles.campaignName}>{camp.name}</span>
                </td>
                <td>
                  <span className={`${styles.badge} ${camp.type === 'Push' ? styles.badgePush : styles.badgeEmail}`}>
                    {camp.type}
                  </span>
                </td>
                <td style={{ color: 'var(--color-text-secondary)' }}>{camp.sent}</td>
                <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{camp.opened}</td>
                <td style={{ color: 'var(--color-text-muted)' }}>{camp.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
              <Button variant="secondary" onClick={() => {
                if (newCampaign.name.trim()) {
                  setCampaignsState([
                    {
                      id: Date.now(),
                      name: newCampaign.name,
                      type: newCampaign.type,
                      sent: 0,
                      opened: 0,
                      date: 'Justo ahora'
                    },
                    ...campaignsState
                  ]);
                  setIsModalOpen(false);
                }
              }}>
                Guardar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
