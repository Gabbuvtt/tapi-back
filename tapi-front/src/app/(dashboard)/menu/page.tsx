'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, GripVertical, Image as ImageIcon, Trash2, Edit2 } from 'lucide-react';
import styles from './menu.module.css';

const categories = ['Bebidas Calientes', 'Postres', 'Snacks'];
const initialItems = [
  { id: 1, name: 'Latte Artesanal', price: '3.50', category: 'Bebidas Calientes', available: true },
  { id: 2, name: 'Cappuccino Clásico', price: '3.00', category: 'Bebidas Calientes', available: true },
  { id: 3, name: 'Brownie de Chocolate', price: '4.50', category: 'Postres', available: true },
];

export default function MenuEditorPage() {
  const [cats, setCats] = useState(categories);
  const [activeCat, setActiveCat] = useState('Bebidas Calientes');
  const [items, setItems] = useState(initialItems);

  // Modals state
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState<any>(null);

  const [isCatModalOpen, setIsCatModalOpen] = useState(false);
  const [newCatName, setNewCatName] = useState('');

  // Drag and Drop State
  const [draggedItem, setDraggedItem] = useState<any>(null);
  const [dragOverItem, setDragOverItem] = useState<any>(null);

  // Handlers
  const handleSaveProduct = () => {
    if (editingProduct.id) {
      setItems(items.map(i => i.id === editingProduct.id ? editingProduct : i));
    } else {
      setItems([...items, { ...editingProduct, id: Date.now() }]);
    }
    setIsProductModalOpen(false);
  };

  const confirmDelete = () => {
    setItems(items.filter(i => i.id !== productToDelete.id));
    setIsDeleteModalOpen(false);
    setProductToDelete(null);
  };

  const handleSaveCategory = () => {
    if (newCatName.trim()) {
      setCats([...cats, newCatName.trim()]);
      setActiveCat(newCatName.trim());
      setNewCatName('');
    }
    setIsCatModalOpen(false);
  };

  const handleDragStart = (e: React.DragEvent, item: any) => {
    setDraggedItem(item);
  };

  const handleDragEnter = (e: React.DragEvent, item: any) => {
    e.preventDefault();
    setDragOverItem(item);
  };

  const handleDragEnd = (e: React.DragEvent) => {
    if (draggedItem && dragOverItem && draggedItem.id !== dragOverItem.id) {
      const draggedIdx = items.findIndex(i => i.id === draggedItem.id);
      const overIdx = items.findIndex(i => i.id === dragOverItem.id);
      
      const newItems = [...items];
      const [dragged] = newItems.splice(draggedIdx, 1);
      newItems.splice(overIdx, 0, dragged);
      
      setItems(newItems);
    }
    setDraggedItem(null);
    setDragOverItem(null);
  };

  return (
    <>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Editor de Menú</h1>
          <p className={styles.subtitle}>Configura el menú digital que verán tus clientes al escanear</p>
        </div>
        <Button 
          leftIcon={<Plus size={18} />} 
          variant="secondary"
          onClick={() => {
            setEditingProduct({ name: '', price: '', category: activeCat, available: true });
            setIsProductModalOpen(true);
          }}
        >
          Nuevo Producto
        </Button>
      </div>

      <div className={styles.editorLayout}>
        <div className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h3 className={styles.sidebarTitle}>Categorías</h3>
            <button className={styles.addButton} onClick={() => setIsCatModalOpen(true)}><Plus size={18} /></button>
          </div>
          <div className={styles.catList}>
            {cats.map(cat => (
              <button 
                key={cat}
                onClick={() => setActiveCat(cat)}
                className={`${styles.catButton} ${activeCat === cat ? styles.catActive : ''}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.mainContent}>
          <div className={styles.itemsList}>
            {items.filter(i => i.category === activeCat).map(item => (
              <div 
                key={item.id} 
                className={`${styles.itemRow} ${draggedItem?.id === item.id ? styles.dragging : ''}`}
                draggable
                onDragStart={(e) => handleDragStart(e, item)}
                onDragEnter={(e) => handleDragEnter(e, item)}
                onDragEnd={handleDragEnd}
                onDragOver={(e) => e.preventDefault()}
              >
                <div className={styles.itemLeft}>
                  <div className={styles.dragHandle}>
                    <GripVertical size={20} />
                  </div>
                  <div className={styles.imagePlaceholder}>
                    <ImageIcon size={24} strokeWidth={1.5} />
                  </div>
                  <div className={styles.itemInfo}>
                    <div className={styles.itemName}>{item.name}</div>
                    <div className={styles.itemPrice}>${item.price}</div>
                  </div>
                </div>
                
                <div className={styles.itemActions}>
                  <div 
                    className={styles.toggleWrapper}
                    onClick={() => {
                      setItems(items.map(i => i.id === item.id ? { ...i, available: !i.available } : i));
                    }}
                  >
                    <div className={`${styles.toggleTrack} ${item.available ? styles.toggleTrackActive : ''}`}>
                      <div className={styles.toggleThumb}></div>
                    </div>
                    <span className={styles.toggleLabel}>Disponible</span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button 
                      className={styles.actionBtn}
                      onClick={() => {
                        setEditingProduct({ ...item });
                        setIsProductModalOpen(true);
                      }}
                    >
                      <Edit2 size={18} />
                    </button>
                    <button 
                      className={`${styles.actionBtn} ${styles.actionBtnDelete}`}
                      onClick={() => {
                        setProductToDelete(item);
                        setIsDeleteModalOpen(true);
                      }}
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal Producto */}
      {isProductModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>
              {editingProduct?.id ? 'Editar Producto' : 'Nuevo Producto'}
            </h2>
            
            <div className={styles.formGroup}>
              <label className={styles.label}>Nombre del Producto</label>
              <input 
                type="text" 
                className={styles.input} 
                value={editingProduct?.name || ''}
                onChange={(e) => setEditingProduct({...editingProduct, name: e.target.value})}
                placeholder="Ej. Latte Artesanal" 
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Precio ($)</label>
              <input 
                type="number" 
                className={styles.input} 
                value={editingProduct?.price || ''}
                onChange={(e) => setEditingProduct({...editingProduct, price: e.target.value})}
                placeholder="0.00" 
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Estado</label>
              <div 
                className={styles.toggleWrapper}
                onClick={() => setEditingProduct({...editingProduct, available: !editingProduct?.available})}
              >
                <div className={`${styles.toggleTrack} ${editingProduct?.available ? styles.toggleTrackActive : ''}`}>
                  <div className={styles.toggleThumb}></div>
                </div>
                <span className={styles.toggleLabel}>
                  {editingProduct?.available ? 'Disponible' : 'Agotado'}
                </span>
              </div>
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsProductModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveProduct}>Guardar</Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Eliminar */}
      {isDeleteModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal} style={{ maxWidth: '400px' }}>
            <h2 className={styles.modalTitle} style={{ color: 'var(--color-error)' }}>
              Eliminar Producto
            </h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-xl)', fontSize: '14px' }}>
              ¿Estás seguro que deseas eliminar <strong>{productToDelete?.name}</strong>? Esta acción no se puede deshacer.
            </p>
            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsDeleteModalOpen(false)}>Cancelar</Button>
              <Button onClick={confirmDelete} style={{ backgroundColor: 'var(--color-error)', color: 'white' }}>
                Eliminar
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Nueva Categoría */}
      {isCatModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal} style={{ maxWidth: '400px' }}>
            <h2 className={styles.modalTitle}>Nueva Categoría</h2>
            <div className={styles.formGroup}>
              <label className={styles.label}>Nombre de la Categoría</label>
              <input 
                type="text" 
                className={styles.input} 
                value={newCatName}
                onChange={(e) => setNewCatName(e.target.value)}
                placeholder="Ej. Promociones"
                autoFocus
              />
            </div>
            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsCatModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveCategory} disabled={!newCatName.trim()}>
                Guardar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
