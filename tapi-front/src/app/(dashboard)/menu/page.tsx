'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Plus, GripVertical, Image as ImageIcon, Trash2, Edit2 } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './menu.module.css';

export default function MenuEditorPage() {
  const [storeId, setStoreId] = useState<string | null>(null);
  const [cats, setCats] = useState<any[]>([]);
  const [activeCat, setActiveCat] = useState<any>(null);
  const [items, setItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modals state
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any>(null);
  const [isSavingProduct, setIsSavingProduct] = useState(false);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState<any>(null);

  const [isCatModalOpen, setIsCatModalOpen] = useState(false);
  const [newCatName, setNewCatName] = useState('');
  const [isSavingCat, setIsSavingCat] = useState(false);

  // Drag and Drop State
  const [draggedItem, setDraggedItem] = useState<any>(null);
  const [dragOverItem, setDragOverItem] = useState<any>(null);

  useEffect(() => {
    async function loadMenu() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        setStoreId(store.id);
        
        // Cargar Categorías
        const { data: categories } = await supabase
          .from('menu_categories')
          .select('*')
          .eq('store_id', store.id)
          .order('order_index', { ascending: true });
          
        if (categories && categories.length > 0) {
          setCats(categories);
          setActiveCat(categories[0]);
        }
        
        // Cargar Items
        const { data: products } = await supabase
          .from('menu_items')
          .select('*')
          .in('category_id', categories ? categories.map(c => c.id) : []);
          
        if (products) {
          setItems(products);
        }
      }
      setIsLoading(false);
    }
    loadMenu();
  }, []);

  // Handlers
  const handleSaveProduct = async () => {
    if (!editingProduct.name || !editingProduct.price) return;
    setIsSavingProduct(true);
    
    const payload = {
      category_id: activeCat.id,
      name: editingProduct.name,
      price: parseFloat(editingProduct.price),
      is_available: editingProduct.is_available
    };

    try {
      if (editingProduct.id) {
        await supabase.from('menu_items').update(payload).eq('id', editingProduct.id);
        setItems(items.map(i => i.id === editingProduct.id ? { ...i, ...payload } : i));
      } else {
        const { data } = await supabase.from('menu_items').insert(payload).select().single();
        if (data) setItems([...items, data]);
      }
      setIsProductModalOpen(false);
    } catch (e) {
      console.error(e);
      alert('Error guardando producto');
    }
    setIsSavingProduct(false);
  };

  const confirmDelete = async () => {
    try {
      await supabase.from('menu_items').delete().eq('id', productToDelete.id);
      setItems(items.filter(i => i.id !== productToDelete.id));
      setIsDeleteModalOpen(false);
      setProductToDelete(null);
    } catch (e) {
      console.error(e);
      alert('Error al borrar');
    }
  };

  const handleSaveCategory = async () => {
    if (newCatName.trim() && storeId) {
      setIsSavingCat(true);
      try {
        const { data } = await supabase.from('menu_categories').insert({
          store_id: storeId,
          name: newCatName.trim(),
          order_index: cats.length
        }).select().single();
        
        if (data) {
          setCats([...cats, data]);
          setActiveCat(data);
          setNewCatName('');
        }
        setIsCatModalOpen(false);
      } catch (e) {
        console.error(e);
        alert('Error al crear categoría');
      }
      setIsSavingCat(false);
    }
  };

  const toggleAvailability = async (item: any) => {
    const newStatus = !item.is_available;
    setItems(items.map(i => i.id === item.id ? { ...i, is_available: newStatus } : i));
    await supabase.from('menu_items').update({ is_available: newStatus }).eq('id', item.id);
  };

  // Drag logic (solo UI por ahora)
  const handleDragStart = (e: React.DragEvent, item: any) => setDraggedItem(item);
  const handleDragEnter = (e: React.DragEvent, item: any) => { e.preventDefault(); setDragOverItem(item); };
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

  if (isLoading) return <div>Cargando Menú...</div>;

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
          disabled={!activeCat}
          onClick={() => {
            setEditingProduct({ name: '', price: '', category_id: activeCat?.id, is_available: true });
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
                key={cat.id}
                onClick={() => setActiveCat(cat)}
                className={`${styles.catButton} ${activeCat?.id === cat.id ? styles.catActive : ''}`}
              >
                {cat.name}
              </button>
            ))}
            {cats.length === 0 && <div className="text-gray-500 text-sm mt-4">Añade una categoría para empezar</div>}
          </div>
        </div>

        <div className={styles.mainContent}>
          <div className={styles.itemsList}>
            {items.filter(i => i.category_id === activeCat?.id).map(item => (
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
                    onClick={() => toggleAvailability(item)}
                  >
                    <div className={`${styles.toggleTrack} ${item.is_available ? styles.toggleTrackActive : ''}`}>
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
            {activeCat && items.filter(i => i.category_id === activeCat.id).length === 0 && (
              <div className="text-center py-10 text-gray-500">No hay productos en esta categoría.</div>
            )}
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
                onClick={() => setEditingProduct({...editingProduct, is_available: !editingProduct?.is_available})}
              >
                <div className={`${styles.toggleTrack} ${editingProduct?.is_available ? styles.toggleTrackActive : ''}`}>
                  <div className={styles.toggleThumb}></div>
                </div>
                <span className={styles.toggleLabel}>
                  {editingProduct?.is_available ? 'Disponible' : 'Agotado'}
                </span>
              </div>
            </div>

            <div className={styles.modalActions}>
              <Button variant="ghost" onClick={() => setIsProductModalOpen(false)}>Cancelar</Button>
              <Button variant="secondary" onClick={handleSaveProduct} isLoading={isSavingProduct}>Guardar</Button>
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
              <Button variant="secondary" onClick={handleSaveCategory} isLoading={isSavingCat} disabled={!newCatName.trim()}>
                Guardar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
