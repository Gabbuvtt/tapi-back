'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Settings, Users, ArrowRight, Edit2, ChevronDown } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './loyalty.module.css';

export default function LoyaltyPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [storeId, setStoreId] = useState<string | null>(null);
  
  // States from DB
  const [programData, setProgramData] = useState({
    stamps_required: 10,
    reward_title: '1 Café Gratis'
  });
  
  // Total cards active (mocked count or from DB)
  const [activeCardsCount, setActiveCardsCount] = useState(0);

  const [isProgramModalOpen, setIsProgramModalOpen] = useState(false);
  
  // Edit State
  const [editStamps, setEditStamps] = useState(10);
  const [editReward, setEditReward] = useState('1 Café Gratis');

  useEffect(() => {
    async function loadLoyalty() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        setStoreId(store.id);
        
        const { data: program } = await supabase
          .from('loyalty_programs')
          .select('stamps_required, reward_title')
          .eq('store_id', store.id)
          .single();
          
        if (program) {
          setProgramData(program);
          setEditStamps(program.stamps_required);
          setEditReward(program.reward_title);
        }

        // Count active cards
        const { count } = await supabase
          .from('loyalty_cards')
          .select('*', { count: 'exact', head: true })
          .eq('store_id', store.id);
          
        setActiveCardsCount(count || 0);
      }
      setIsLoading(false);
    }
    loadLoyalty();
  }, []);

  const handleSaveProgram = async () => {
    setIsSaving(true);
    try {
      await supabase.from('loyalty_programs').upsert({
        store_id: storeId,
        stamps_required: editStamps,
        reward_title: editReward
      }, { onConflict: 'store_id' });
      
      setProgramData({
        stamps_required: editStamps,
        reward_title: editReward
      });
      setIsProgramModalOpen(false);
      alert('Programa actualizado con éxito');
    } catch (err) {
      console.error(err);
      alert('Error guardando el programa');
    }
    setIsSaving(false);
  };

  if (isLoading) return <div>Cargando Programa...</div>;

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Programa de Lealtad</h1>
      </div>

      <div className={styles.pageLayout}>
        {/* Columna Izquierda: Ajustes del Programa */}
        <div>
          <h2 className={styles.sectionTitle}>Reglas Actuales</h2>
          <div className={styles.activeProgramCard}>
            <div className={styles.programInfo}>
              <div className="flex justify-between items-center mb-2">
                <h3>Tarjeta de Sellos NFC</h3>
                <span className={`${styles.badge} ${styles.badgeActive}`}>Activo</span>
              </div>
              
              <div className={styles.programMeta}>
                <div className={styles.metaItem}>
                  <Settings size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Mecánica</div>
                    <div>1 Sello por Tap NFC</div>
                  </div>
                </div>
                <div className={styles.metaItem}>
                  <ArrowRight size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Meta</div>
                    <div>{programData.stamps_required} sellos requeridos</div>
                  </div>
                </div>
                <div className={styles.metaItem}>
                  <Users size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Rendimiento</div>
                    <div>{activeCardsCount} clientes activos</div>
                  </div>
                </div>
              </div>
            </div>
            
            <Button variant="outline" className="w-full" onClick={() => setIsProgramModalOpen(true)}>
              Modificar Reglas
            </Button>
          </div>
        </div>

        {/* Columna Derecha: Recompensas */}
        <div>
          <h2 className={styles.sectionTitle}>Recompensa Final</h2>
          <div className={styles.rewardsGrid}>
            <div className={`${styles.rewardCard}`}>
              <div className={styles.rewardHeader}>
                <div className={styles.rewardTitle}>{programData.reward_title}</div>
                <div className={styles.rewardCost}>{programData.stamps_required} sellos</div>
              </div>
              <div className={styles.rewardDesc}>El premio que recibe tu cliente al completar la tarjeta.</div>
              <div className={styles.rewardFooter}>
                <span className={`${styles.badge} ${styles.badgeActive}`}>
                  Activo
                </span>
                <button className={styles.editButton} onClick={() => setIsProgramModalOpen(true)}>
                  <Edit2 size={14} /> Editar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Programa */}
      {isProgramModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>Configuración del Programa</h2>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Visitas Requeridas para Completar Tarjeta</label>
              <div className={styles.selectWrapper}>
                <select 
                  className={styles.input} 
                  value={editStamps}
                  onChange={(e) => setEditStamps(Number(e.target.value))}
                >
                  <option value={5}>5 Sellos</option>
                  <option value={8}>8 Sellos</option>
                  <option value={10}>10 Sellos</option>
                  <option value={12}>12 Sellos</option>
                </select>
                <ChevronDown size={16} className={styles.selectIcon} />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Premio Final al Completar</label>
              <input 
                type="text" 
                className={styles.input} 
                value={editReward} 
                onChange={(e) => setEditReward(e.target.value)}
                placeholder="Ej: 1 Bebida Gratis"
              />
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsProgramModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveProgram} isLoading={isSaving}>Guardar Cambios</Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
