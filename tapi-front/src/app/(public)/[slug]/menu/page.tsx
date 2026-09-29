'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Coffee } from 'lucide-react';
import styles from './menu.module.css';

// Mock Data
const categories = ['Todos', 'Bebidas Calientes', 'Bebidas Frías', 'Postres', 'Snacks'];

const menuItems = [
  { id: 1, name: 'Latte Artesanal', desc: 'Espresso doble con leche texturizada y arte latte.', price: 3.50, category: 'Bebidas Calientes', tags: ['Popular'], available: true },
  { id: 2, name: 'Cappuccino Clásico', desc: 'Partes iguales de espresso, leche al vapor y espuma.', price: 3.00, category: 'Bebidas Calientes', tags: [], available: true },
  { id: 3, name: 'Smoothie Verde', desc: 'Espinaca, manzana verde, apio y jengibre.', price: 5.00, category: 'Bebidas Frías', tags: ['Vegano', 'Sin Gluten'], available: true },
  { id: 4, name: 'Brownie de Chocolate', desc: 'Brownie melcochudo con trozos de chocolate amargo.', price: 4.50, category: 'Postres', tags: [], available: true },
  { id: 5, name: 'Tarta de Limón', desc: 'Base de galleta con crema de limón y merengue tostado.', price: 4.00, category: 'Postres', tags: [], available: false },
];

export default function MenuPage({ params }: { params: { slug: string } }) {
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState('Todos');

  const filteredItems = activeCategory === 'Todos' 
    ? menuItems 
    : menuItems.filter(item => item.category === activeCategory);

  return (
    <div className={styles.container}>
      <nav className={styles.topNav}>
        <button className={styles.backBtn} onClick={() => router.back()}>
          <ArrowLeft size={24} />
        </button>
        <div className={styles.headerInfo}>
          <h1 className={styles.pageTitle}>Menú Digital</h1>
          <div className={styles.businessName}>Café El Aroma</div>
        </div>
      </nav>

      <div className={styles.categoriesWrapper}>
        <div className={styles.categoriesList}>
          {categories.map(cat => (
            <button 
              key={cat}
              className={`${styles.categoryChip} ${activeCategory === cat ? styles.categoryChipActive : ''}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.menuList}>
        {filteredItems.map(item => (
          <div key={item.id} className={styles.menuItemCard}>
            <div className={styles.itemImagePlaceholder}>
              <Coffee size={32} />
            </div>
            <div className={styles.itemInfo}>
              <div className={styles.itemHeader}>
                <div className={styles.itemName}>{item.name}</div>
                <div className={styles.itemPrice}>${item.price.toFixed(2)}</div>
              </div>
              <p className={styles.itemDesc}>{item.desc}</p>
              
              <div className={styles.itemFooter}>
                <div className={styles.tags}>
                  {item.tags.map(tag => (
                    <span key={tag} className={styles.tagChip}>{tag}</span>
                  ))}
                </div>
                {item.available ? (
                  <div className={styles.availability}>
                    <span className={styles.dot}></span>
                    Disponible
                  </div>
                ) : (
                  <div className="text-xs text-red-500 font-medium flex items-center gap-1">
                    Agotado
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {filteredItems.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No hay productos en esta categoría.
          </div>
        )}
      </div>
    </div>
  );
}
