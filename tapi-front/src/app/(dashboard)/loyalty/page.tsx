'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, Settings, Users, ArrowRight, Edit2, ChevronDown, Trash2 } from 'lucide-react';
import styles from './loyalty.module.css';

// Mock Data
const initialProgram = {
  name: 'Café Lovers',
  type: 'Visitas',
  requiredVisits: 10,
  activeCards: 342
};

const initialRewards = [
  { id: 1, title: '10% Descuento', desc: 'En toda la compra', cost: 10, type: 'discount_pct', status: 'active' },
  { id: 2, title: 'Café Gratis', desc: 'Un capuccino o latte tamaño mediano', cost: 15, type: 'free_item', status: 'active' },
  { id: 3, title: '2x1 en Postres', desc: 'Compra un postre y llévate el segundo gratis', cost: 8, type: 'custom', status: 'inactive' },
];

export default function LoyaltyPage() {
  const [activeProgram, setActiveProgram] = useState(initialProgram);
  const [rewards, setRewards] = useState(initialRewards);
  
  // Modals state
  const [isRewardModalOpen, setIsRewardModalOpen] = useState(false);
  const [editingReward, setEditingReward] = useState<any>(null);
  
  const [isProgramModalOpen, setIsProgramModalOpen] = useState(false);

  // Rewards logic
  const openNewRewardModal = () => {
    setEditingReward({ status: 'active', title: '', desc: '', cost: 10 });
    setIsRewardModalOpen(true);
  };

  const openEditRewardModal = (reward: any) => {
    setEditingReward({ ...reward });
    setIsRewardModalOpen(true);
  };

  const handleSaveReward = () => {
    if (editingReward.id) {
      setRewards(rewards.map(r => r.id === editingReward.id ? editingReward : r));
    } else {
      setRewards([...rewards, { ...editingReward, id: Date.now() }]);
    }
    setIsRewardModalOpen(false);
  };

  const handleDeleteReward = () => {
    if (editingReward.id) {
      setRewards(rewards.filter(r => r.id !== editingReward.id));
    }
    setIsRewardModalOpen(false);
  };

  // Program logic
  const handleSaveProgram = () => {
    setIsProgramModalOpen(false);
    // TODO: implement API save
  };

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Programa de Lealtad</h1>
        <Button leftIcon={<Plus size={18} />} variant="secondary" onClick={openNewRewardModal}>
          Nuevo Reward
        </Button>
      </div>

      <div className={styles.pageLayout}>
        {/* Columna Izquierda: Ajustes del Programa */}
        <div>
          <h2 className={styles.sectionTitle}>Ajustes del Programa</h2>
          <div className={styles.activeProgramCard}>
            <div className={styles.programInfo}>
              <div className="flex justify-between items-center mb-2">
                <h3>{activeProgram.name}</h3>
                <span className={`${styles.badge} ${styles.badgeActive}`}>Activo</span>
              </div>
              
              <div className={styles.programMeta}>
                <div className={styles.metaItem}>
                  <Settings size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Mecánica</div>
                    <div>Por {activeProgram.type}</div>
                  </div>
                </div>
                <div className={styles.metaItem}>
                  <ArrowRight size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Meta</div>
                    <div>{activeProgram.requiredVisits} visitas requeridas</div>
                  </div>
                </div>
                <div className={styles.metaItem}>
                  <Users size={18} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="font-semibold text-[var(--color-text-primary)]">Rendimiento</div>
                    <div>{activeProgram.activeCards} tarjetas activas</div>
                  </div>
                </div>
              </div>
            </div>
            
            <Button variant="outline" className="w-full" onClick={() => setIsProgramModalOpen(true)}>
              Editar Programa
            </Button>
          </div>
        </div>

        {/* Columna Derecha: Recompensas */}
        <div>
          <h2 className={styles.sectionTitle}>Recompensas Configuradas</h2>
          <div className={styles.rewardsGrid}>
            {rewards.map(reward => (
              <div key={reward.id} className={`${styles.rewardCard} ${reward.status === 'inactive' ? 'opacity-50' : ''}`}>
                <div className={styles.rewardHeader}>
                  <div className={styles.rewardTitle}>{reward.title}</div>
                  <div className={styles.rewardCost}>{reward.cost} pts</div>
                </div>
                <div className={styles.rewardDesc}>{reward.desc}</div>
                <div className={styles.rewardFooter}>
                  <span className={`${styles.badge} ${reward.status === 'active' ? styles.badgeActive : styles.badgeInactive}`}>
                    {reward.status === 'active' ? 'Activo' : 'Inactivo'}
                  </span>
                  <button className={styles.editButton} onClick={() => openEditRewardModal(reward)}>
                    <Edit2 size={14} /> Editar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal Recompensas */}
      {isRewardModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
              <h2 className={styles.modalTitle} style={{ marginBottom: 0 }}>
                {editingReward.id ? 'Editar Reward' : 'Nuevo Reward'}
              </h2>
              {editingReward.id && (
                <div 
                  role="button" 
                  tabIndex={0}
                  onClick={handleDeleteReward} 
                  className={styles.actionBtnDelete}
                >
                  <Trash2 size={18} />
                </div>
              )}
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Título de la Recompensa</label>
              <input 
                type="text" 
                className={styles.input} 
                value={editingReward?.title} 
                onChange={(e) => setEditingReward({...editingReward, title: e.target.value})}
                placeholder="Ej. Café Gratis" 
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Descripción</label>
              <input 
                type="text" 
                className={styles.input} 
                value={editingReward?.desc} 
                onChange={(e) => setEditingReward({...editingReward, desc: e.target.value})}
                placeholder="Breve detalle..." 
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Costo (Puntos/Sellos)</label>
              <input 
                type="number" 
                className={styles.input} 
                value={editingReward?.cost} 
                onChange={(e) => setEditingReward({...editingReward, cost: Number(e.target.value)})}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Estado</label>
              <div 
                className={styles.toggleWrapper}
                onClick={() => setEditingReward({...editingReward, status: editingReward?.status === 'active' ? 'inactive' : 'active'})}
              >
                <div className={`${styles.toggleTrack} ${editingReward?.status === 'active' ? styles.toggleTrackActive : ''}`}>
                  <div className={styles.toggleThumb}></div>
                </div>
                <span className={styles.toggleLabel}>
                  {editingReward?.status === 'active' ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsRewardModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveReward}>Guardar</Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Programa */}
      {isProgramModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>Configuración del Programa</h2>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Nombre del Programa</label>
              <input 
                type="text" 
                className={styles.input} 
                defaultValue={activeProgram.name} 
              />
            </div>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Tipo de Mecánica</label>
              <div className={styles.selectWrapper}>
                <select className={styles.input} defaultValue={activeProgram.type}>
                  <option value="Visitas">Visitas (1 sello por compra)</option>
                  <option value="Puntos">Puntos (por monto de compra)</option>
                </select>
                <ChevronDown size={16} className={styles.selectIcon} />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Visitas Requeridas para Completar Tarjeta</label>
              <input 
                type="number" 
                className={styles.input} 
                defaultValue={activeProgram.requiredVisits} 
              />
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsProgramModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveProgram}>Guardar</Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
