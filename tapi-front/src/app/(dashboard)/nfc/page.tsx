'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, Tag, Smartphone, MoreVertical } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './nfc.module.css';

export default function NfcPage() {
  const [storeId, setStoreId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<any>(null);
  const [tagsState, setTagsState] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    async function loadNfc() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        setStoreId(store.id);
        const { data: tags } = await supabase
          .from('nfc_tags')
          .select('*')
          .eq('store_id', store.id)
          .order('created_at', { ascending: false });
          
        if (tags) {
          setTagsState(tags);
        }
      }
      setIsLoading(false);
    }
    loadNfc();
  }, []);

  const handleSave = async () => {
    if (!editingTag.name) return;
    setIsSaving(true);
    
    try {
      if (editingTag.id) {
        await supabase.from('nfc_tags').update({
          name: editingTag.name,
          location: editingTag.location,
          status: editingTag.status
        }).eq('id', editingTag.id);
        
        setTagsState(tagsState.map(t => t.id === editingTag.id ? { ...t, ...editingTag } : t));
      } else {
        const { data } = await supabase.from('nfc_tags').insert({
          store_id: storeId,
          name: editingTag.name,
          location: editingTag.location || 'Sticker',
          tag_identifier: `NFC-${Math.floor(Math.random() * 10000)}`, // Generado auto en MVP
          status: 'active'
        }).select().single();
        
        if (data) setTagsState([data, ...tagsState]);
      }
      setIsModalOpen(false);
    } catch (e) {
      console.error(e);
      alert('Error al guardar la etiqueta');
    }
    setIsSaving(false);
  };

  if (isLoading) return <div>Cargando Etiquetas...</div>;

  return (
    <>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Etiquetas NFC</h1>
          <p className={styles.subtitle}>Gestiona los puntos físicos de escaneo en tu local</p>
        </div>
        <Button leftIcon={<Plus size={18} />} variant="secondary" onClick={() => {
          setEditingTag({ name: '', location: 'Sticker', status: 'active' });
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
                <div className={styles.statValue}>{tagsState.length}</div>
                <div className={styles.statLabel}>Etiquetas Vinculadas</div>
              </div>
            </div>
            <div className={styles.statBox}>
              <div className={styles.statIcon} style={{ background: 'rgba(22, 163, 74, 0.1)', color: 'var(--color-success)' }}><Smartphone size={20} /></div>
              <div>
                <div className={styles.statValue}>0</div>
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
                {tagsState.length > 0 ? tagsState.map(tag => (
                  <tr key={tag.id}>
                    <td className={styles.nameCell}>
                      <div className={styles.iconWrapper}><Tag size={16} /></div>
                      <span className="font-semibold">{tag.name}</span>
                    </td>
                    <td>{tag.location}</td>
                    <td className="font-medium text-[var(--color-primary)]">0</td>
                    <td className="text-sm text-gray-500">Nuevo</td>
                    <td>
                      <span className={`${styles.badge} ${tag.status === 'active' ? styles.badgeActive : styles.badgeInactive}`}>
                        {tag.status === 'active' ? 'Activa' : 'Inactiva'}
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
                )) : (
                  <tr>
                    <td colSpan={6} className="text-center py-4 text-gray-500">No hay etiquetas vinculadas.</td>
                  </tr>
                )}
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
                value={editingTag?.location || 'Sticker'}
                onChange={(e) => setEditingTag({...editingTag, location: e.target.value})}
              >
                <option value="Sticker">Sticker</option>
                <option value="Display">Display de Mesa</option>
                <option value="Cartelera">Cartelera</option>
              </select>
            </div>
            
            {editingTag?.id && (
              <div className={styles.formGroup}>
                <label className={styles.label}>Estado</label>
                <div 
                  className={styles.toggleWrapper}
                  onClick={() => setEditingTag({...editingTag, status: editingTag?.status === 'active' ? 'inactive' : 'active'})}
                >
                  <div className={`${styles.toggleTrack} ${editingTag?.status === 'active' ? styles.toggleTrackActive : ''}`}>
                    <div className={styles.toggleThumb}></div>
                  </div>
                  <span className={styles.toggleLabel}>
                    {editingTag?.status === 'active' ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
              </div>
            )}

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSave} isLoading={isSaving}>
                Guardar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
