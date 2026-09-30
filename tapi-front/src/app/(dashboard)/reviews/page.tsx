'use client';

import React, { useState, useEffect } from 'react';
import { Star, ChevronDown } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './reviews.module.css';

function getBadgeClass(status: string) {
  switch(status) {
    case 'Google': return styles.badgeGoogle;
    case 'Aprobada': return styles.badgeApproved;
    case 'Interna': return styles.badgeInternal;
    default: return styles.badgePending;
  }
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, average: 0, googleCount: 0 });

  useEffect(() => {
    async function loadReviews() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        const { data: reviewData } = await supabase
          .from('reviews')
          .select('*, customers(full_name)')
          .eq('store_id', store.id)
          .order('created_at', { ascending: false });
          
        if (reviewData) {
          setReviews(reviewData);
          
          let sum = 0;
          let googleC = 0;
          reviewData.forEach(r => {
            sum += r.rating;
            if (r.status === 'Google') googleC++;
          });
          
          setStats({
            total: reviewData.length,
            average: reviewData.length > 0 ? (sum / reviewData.length) : 0,
            googleCount: googleC
          });
        }
      }
      setIsLoading(false);
    }
    loadReviews();
  }, []);

  if (isLoading) return <div>Cargando Reseñas...</div>;

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Reseñas</h1>
      </div>

      <div className={styles.statsBar}>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Total Reseñas</div>
          <div className={styles.statValue}>{stats.total}</div>
        </div>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Calificación Promedio</div>
          <div className={styles.statValue}>
            {stats.average.toFixed(1)} <Star fill="var(--color-secondary)" color="var(--color-secondary)" size={28} />
          </div>
        </div>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Enviadas a Google</div>
          <div className={styles.statValue}>{stats.googleCount}</div>
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
        {reviews.length > 0 ? reviews.map(review => (
          <div key={review.id} className={styles.reviewCard}>
            <div className={styles.reviewHeader}>
              <div className={styles.userInfo}>
                <div className={styles.avatar}>{(review.customers?.full_name || 'A')[0]}</div>
                <div>
                  <div className={styles.userName}>{review.customers?.full_name || 'Anónimo'}</div>
                  <div className={styles.date}>{new Date(review.created_at).toLocaleDateString()}</div>
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
        )) : (
          <div className="text-center py-10 text-gray-400">Aún no hay reseñas registradas.</div>
        )}
      </div>
    </>
  );
}
