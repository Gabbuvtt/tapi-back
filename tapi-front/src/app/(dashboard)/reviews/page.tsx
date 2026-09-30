'use client';

import React, { useState, useEffect } from 'react';
import { Star, ChevronDown } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './reviews.module.css';
import PageLoader from '@/components/ui/PageLoader';

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
  const [filteredReviews, setFilteredReviews] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, average: 0, googleCount: 0 });
  const [typeFilter, setTypeFilter] = useState('Todas');
  const [dateFilter, setDateFilter] = useState('30dias');

  // Lógica de filtrado local
  useEffect(() => {
    let result = [...reviews];
    
    // Filtrar por tipo
    if (typeFilter === 'Google') {
      result = result.filter(r => r.status === 'Google');
    } else if (typeFilter === 'Internas') {
      result = result.filter(r => r.status === 'Interna');
    }

    // Filtrar por fecha
    const now = new Date();
    if (dateFilter === 'hoy') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      result = result.filter(r => new Date(r.created_at) >= today);
    } else if (dateFilter === 'semana') {
      const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      result = result.filter(r => new Date(r.created_at) >= lastWeek);
    } else if (dateFilter === 'mes') {
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      result = result.filter(r => new Date(r.created_at) >= startOfMonth);
    } else if (dateFilter === '30dias') {
      const last30 = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      result = result.filter(r => new Date(r.created_at) >= last30);
    }

    setFilteredReviews(result);

    // Actualizar Stats basados en el filtro actual
    let sum = 0;
    let googleC = 0;
    result.forEach(r => {
      sum += r.rating;
      if (r.status === 'Google') googleC++;
    });
    
    setStats({
      total: result.length,
      average: result.length > 0 ? (sum / result.length) : 0,
      googleCount: googleC
    });
  }, [reviews, typeFilter, dateFilter]);

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
        }
      }
      setIsLoading(false);
    }
    loadReviews();
  }, []);

  if (isLoading) return <PageLoader text="Cargando Reseñas..." />;

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
          <select className={styles.select} value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="Todas">Todas las reseñas</option>
            <option value="Google">Enviadas a Google (5★ y 4★)</option>
            <option value="Internas">Internas (1★ a 3★)</option>
          </select>
          <ChevronDown size={14} className={styles.selectIcon} />
        </div>
        <div className={styles.selectWrapper}>
          <select className={styles.select} value={dateFilter} onChange={(e) => setDateFilter(e.target.value)}>
            <option value="siempre">Siempre</option>
            <option value="hoy">Hoy</option>
            <option value="semana">Esta semana (7 días)</option>
            <option value="mes">Este mes actual</option>
            <option value="30dias">Últimos 30 días</option>
          </select>
          <ChevronDown size={14} className={styles.selectIcon} />
        </div>
      </div>

      <div className={styles.reviewsList}>
        {filteredReviews.length > 0 ? filteredReviews.map(review => (
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
