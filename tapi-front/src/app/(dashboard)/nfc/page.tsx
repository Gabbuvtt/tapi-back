'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, Tag, Smartphone, MoreVertical } from 'lucide-react';
import styles from './nfc.module.css';

// Mock Data
const tags = [
  { id: 1, name: 'Mesa 1', type: 'Sticker', status: 'Activa', scans: 145, lastScan: 'Hace 2 horas' },
  { id: 2, name: 'Mesa 2', type: 'Display', status: 'Activa', scans: 89, lastScan: 'Hace 5 horas' },
  { id: 3, name: 'Barra Principal', type: 'Stand', status: 'Inactiva', scans: 12, lastScan: 'Hace 3 días' },
];

export default function NfcPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<any>(null);
  const [tagsState, setTagsState] = useState(tags);

  return (
    <>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Etiquetas NFC</h1>
          <p className={styles.subtitle}>Gestiona los puntos físicos de escaneo en tu local</p>
        </div>
        <Button leftIcon={<Plus size={18} />} variant="secondary" onClick={() => {
          setEditingTag({ name: '', type: 'Sticker', status: 'Activa' });
          setIsModalOpen(true);
        }}>
          Vincular Etiqueta
        </Button>
      </div>

      <div className={styles.pageLayout}>
        {/* Columna Izquierda: Panel de Control NFC */}
        <div>
          <h2 className={styles.sectionTitle}>Resumen de Red</h2>
          <div className={styles.sidebarCard}>
            <div className={styles.statBox}>
              <div className={styles.statIcon}><Tag size={20} /></div>
              <div>
                <div className={styles.statValue}>12</div>
                <div className={styles.statLabel}>Etiquetas Vinculadas</div>
              </div>
            </div>
            <div className={styles.statBox}>
              <div className={styles.statIcon} style={{ background: 'rgba(22, 163, 74, 0.1)', color: 'var(--color-success)' }}><Smartphone size={20} /></div>
              <div>
                <div className={styles.statValue}>246</div>
                <div className={styles.statLabel}>Escaneos este mes</div>
              </div>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Tabla de Etiquetas */}
        <div>
          <h2 className={styles.sectionTitle}>Etiquetas Configuradas</h2>
          <div className={styles.card}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Ubicación/Nombre</th>
                  <th>Formato</th>
                  <th>Escaneos</th>
                  <th>Último Escaneo</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {tagsState.map(tag => (
                  <tr key={tag.id}>
                    <td className={styles.nameCell}>
                      <div className={styles.iconWrapper}><Tag size={16} /></div>
                      <span className="font-semibold">{tag.name}</span>
                    </td>
                    <td>{tag.type}</td>
                    <td className="font-medium text-[var(--color-primary)]">{tag.scans}</td>
                    <td className="text-sm text-gray-500">{tag.lastScan}</td>
                    <td>
                      <span className={`${styles.badge} ${tag.status === 'Activa' ? styles.badgeActive : styles.badgeInactive}`}>
                        {tag.status}
                      </span>
                    </td>
                    <td className="text-right">
                      <div 
                        role="button" 
                        tabIndex={0} 
                        className={styles.actionBtn}
                        onClick={() => {
                          setEditingTag({ ...tag });
                          setIsModalOpen(true);
                        }}
                      >
                        <MoreVertical size={20} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>
              {editingTag?.id ? 'Editar Etiqueta' : 'Vincular Nueva Etiqueta'}
            </h2>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Ubicación (ej: Mesa 3)</label>
              <input 
                type="text" 
                className={styles.input} 
                value={editingTag?.name || ''}
                onChange={(e) => setEditingTag({...editingTag, name: e.target.value})}
                placeholder="Ubicación" 
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Formato</label>
              <select 
                className={styles.input}
                value={editingTag?.type || 'Sticker'}
                onChange={(e) => setEditingTag({...editingTag, type: e.target.value})}
              >
                <option>Sticker</option>
                <option>Display de Mesa</option>
                <option>Cartelera</option>
              </select>
            </div>
            
            {editingTag?.id && (
              <div className={styles.formGroup}>
                <label className={styles.label}>Estado</label>
                <div 
                  className={styles.toggleWrapper}
                  onClick={() => setEditingTag({...editingTag, status: editingTag?.status === 'Activa' ? 'Inactiva' : 'Activa'})}
                >
                  <div className={`${styles.toggleTrack} ${editingTag?.status === 'Activa' ? styles.toggleTrackActive : ''}`}>
                    <div className={styles.toggleThumb}></div>
                  </div>
                  <span className={styles.toggleLabel}>
                    {editingTag?.status}
                  </span>
                </div>
              </div>
            )}

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={() => {
                if (editingTag.id) {
                  setTagsState(tagsState.map(t => t.id === editingTag.id ? editingTag : t));
                } else {
                  setTagsState([...tagsState, { ...editingTag, id: Date.now(), scans: 0, lastScan: 'Nuevo' }]);
                }
                setIsModalOpen(false);
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
