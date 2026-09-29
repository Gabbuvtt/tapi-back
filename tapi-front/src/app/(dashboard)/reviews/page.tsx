'use client';

import React from 'react';
import { Star, ChevronDown } from 'lucide-react';
import styles from './reviews.module.css';

// Mock Data
const reviews = [
  { id: 1, name: 'Juan Pérez', rating: 5, comment: 'Excelente servicio, siempre vuelvo por el mejor café de la ciudad.', status: 'Google', date: 'Hace 2 horas' },
  { id: 2, name: 'María López', rating: 4, comment: 'Muy buen café, ambiente agradable. Me gustaría que tuvieran más opciones veganas.', status: 'Aprobada', date: 'Hace 5 horas' },
  { id: 3, name: 'Carlos R.', rating: 3, comment: 'El servicio podría mejorar un poco en horas pico.', status: 'Interna', date: 'Hace 1 día' },
  { id: 4, name: 'Ana M.', rating: 5, comment: 'Los mejores postres, me encantó la tarta de manzana.', status: 'Pendiente', date: 'Hace 2 días' },
];

function getBadgeClass(status: string) {
  switch(status) {
    case 'Google': return styles.badgeGoogle;
    case 'Aprobada': return styles.badgeApproved;
    case 'Interna': return styles.badgeInternal;
    default: return styles.badgePending;
  }
}

export default function ReviewsPage() {
  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Reseñas</h1>
      </div>

      <div className={styles.statsBar}>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Total Reseñas</div>
          <div className={styles.statValue}>89</div>
        </div>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Calificación Promedio</div>
          <div className={styles.statValue}>
            4.7 <Star fill="var(--color-secondary)" color="var(--color-secondary)" size={28} />
          </div>
        </div>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Enviadas a Google</div>
          <div className={styles.statValue}>52</div>
        </div>
      </div>

      <div className={styles.filters}>
        <div className={styles.selectWrapper}>
          <select className={styles.select}>
            <option>Todas las reseñas</option>
            <option>Enviadas a Google (5★ y 4★)</option>
            <option>Internas (1★ a 3★)</option>
            <option>Pendientes de revisión</option>
          </select>
          <ChevronDown size={14} className={styles.selectIcon} />
        </div>
        <div className={styles.selectWrapper}>
          <select className={styles.select}>
            <option>Últimos 30 días</option>
            <option>Este mes</option>
          </select>
          <ChevronDown size={14} className={styles.selectIcon} />
        </div>
      </div>

      <div className={styles.reviewsList}>
        {reviews.map(review => (
          <div key={review.id} className={styles.reviewCard}>
            <div className={styles.reviewHeader}>
              <div className={styles.userInfo}>
                <div className={styles.avatar}>{review.name[0]}</div>
                <div>
                  <div className={styles.userName}>{review.name}</div>
                  <div className={styles.date}>{review.date}</div>
                </div>
              </div>
              <span className={`${styles.badge} ${getBadgeClass(review.status)}`}>
                {review.status}
              </span>
            </div>
            
            <div className={styles.rating}>
              {[...Array(5)].map((_, i) => (
                <Star 
                  key={i} 
                  size={16} 
                  fill={i < review.rating ? "currentColor" : "none"} 
                  color={i < review.rating ? "currentColor" : "var(--color-border-strong)"}
                />
              ))}
            </div>
            
            <p className={styles.comment}>{review.comment}</p>
          </div>
        ))}
      </div>
    </>
  );
}
