'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, ChevronDown } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { supabase } from '@/lib/supabase';
import styles from './dashboard.module.css';

// La gráfica iniciará vacía hasta que conectemos los módulos NFC reales
const chartData: any[] = [];

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalTaps: 0,
    customers: 0,
    avgReview: '0.0'
  });
  
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [dateFilter, setDateFilter] = useState('30dias');
  
  // Guardar raw data para no volver a llamar a DB al cambiar filtro
  const [rawData, setRawData] = useState<{cards: any[], reviews: any[]}>({ cards: [], reviews: [] });

  useEffect(() => {
    async function loadDashboard() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data: store } = await supabase
        .from('stores')
        .select('id')
        .eq('owner_email', session.user.email)
        .single();
        
      if (store) {
        // Fetch loyalty cards para sumar todos los sellos (Taps Totales) y Clientes únicos
        const { data: cards } = await supabase
          .from('loyalty_cards')
          .select('stamps_count, created_at, customers(full_name)')
          .eq('store_id', store.id);
          
        let taps = 0;
        let activityList: any[] = [];
        
        if (cards) {
          cards.forEach((card: any, idx) => {
            taps += card.stamps_count || 0;
            if (card.stamps_count > 0) {
              activityList.push({
                id: idx,
                action: 'Sello de fidelidad sumado',
                source: card.customers?.full_name || 'Cliente anónimo',
                status: 'Verificado',
                time: 'Reciente'
              });
            }
          });
        }
        
        // Calcular reseñas reales
        const { data: reviews } = await supabase
          .from('reviews')
          .select('rating, created_at')
          .eq('store_id', store.id);
          
        setRawData({
          cards: cards || [],
          reviews: reviews || []
        });
      }
    }
    loadDashboard();
  }, []);

  // Filtrado local según dateFilter
  useEffect(() => {
    const now = new Date();
    let startDate: Date | null = null;
    
    if (dateFilter === 'hoy') {
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    } else if (dateFilter === 'semana') {
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    } else if (dateFilter === 'mes') {
      startDate = new Date(now.getFullYear(), now.getMonth(), 1);
    } else if (dateFilter === '30dias') {
      startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    // Filtrar reseñas
    let filteredReviews = rawData.reviews;
    if (startDate) {
      filteredReviews = filteredReviews.filter(r => new Date(r.created_at) >= startDate!);
    }
    
    let avgScore = 0;
    if (filteredReviews.length > 0) {
      const sum = filteredReviews.reduce((acc, rev) => acc + rev.rating, 0);
      avgScore = sum / filteredReviews.length;
    }
    
    // Filtrar clientes nuevos (loyalty cards creadas)
    let filteredCards = rawData.cards;
    if (startDate) {
      filteredCards = filteredCards.filter(c => new Date(c.created_at) >= startDate!);
    }
    
    // Los taps no se pueden filtrar por fecha aún (no hay historial), así que sumamos el total o los dejamos como globales.
    let taps = 0;
    rawData.cards.forEach(card => { taps += card.stamps_count || 0; });
    
    setStats({
      totalTaps: taps, // Global por ahora
      customers: filteredCards.length,
      avgReview: avgScore > 0 ? avgScore.toFixed(1) : '0.0'
    });
    
  }, [rawData, dateFilter]);

  return (
    <>
      <div className={styles.pageHeader}>
        <h1 className={styles.title}>Overview</h1>
        <div className={styles.filters}>
          <div className={styles.selectWrapper}>
            <select className={styles.select} value={dateFilter} onChange={(e) => setDateFilter(e.target.value)}>
              <option value="siempre">Siempre</option>
              <option value="hoy">Hoy</option>
              <option value="semana">Esta semana</option>
              <option value="mes">Este mes</option>
              <option value="30dias">Últimos 30 días</option>
            </select>
            <ChevronDown size={14} className={styles.selectIcon} />
          </div>
        </div>
      </div>

      <div className={styles.statsGrid}>
        <StatCard 
          title="Taps NFC Totales" 
          value={stats.totalTaps.toString()} 
          trend="+18.4%" 
        />
        <StatCard 
          title="Reviews Google" 
          value={stats.avgReview} 
          trend="Promedio" 
        />
        <StatCard 
          title="Clientes Únicos" 
          value={stats.customers.toString()} 
          trend="Nuevos clientes" 
        />
        <StatCard 
          title="Canjes" 
          value="0" 
          trend="Próximamente" 
        />
      </div>

      <div className={styles.contentGrid}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Actividad NFC en Tiempo Real</h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 0, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Tooltip 
                  cursor={{ stroke: 'var(--color-border)', strokeWidth: 1, strokeDasharray: '4 4' }}
                  contentStyle={{ 
                    backgroundColor: 'var(--color-surface)', 
                    borderRadius: '8px',
                    border: '1px solid var(--color-border)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                  }} 
                />
                {chartData.length > 0 ? (
                  <Area 
                    type="monotone" 
                    dataKey="scans" 
                    stroke="var(--color-primary)" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorScans)" 
                  />
                ) : null}
              </AreaChart>
              {chartData.length === 0 && (
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'var(--color-text-secondary)' }}>
                  Aún no hay datos NFC
                </div>
              )}
            </ResponsiveContainer>
          </div>
          <div className={styles.chartFooter}>
            <div className={styles.chartMetric}>Tiempo prom. a reseña: <span>14s</span></div>
            <div className={styles.chartMetric}>Conversión Tap-a-Wallet: <span>74%</span></div>
          </div>
        </div>

        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Actividad Reciente</h2>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Interacción</th>
                <th>Cliente</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {recentActivity.length > 0 ? recentActivity.map((activity) => (
                <tr key={activity.id}>
                  <td>
                    <div className="font-medium">{activity.action}</div>
                    <div className="text-xs text-gray-500 mt-1">{activity.time}</div>
                  </td>
                  <td className="text-gray-600">{activity.source}</td>
                  <td>
                    <span className={`${styles.badge} ${styles.badgeSuccess}`}>
                      {activity.status}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={3} className="text-center py-4 text-gray-500">No hay actividad reciente</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

// Subcomponente Minimalista
function StatCard({ title, value, trend }: { title: string, value: string, trend: string }) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statHeader}>
        <span className={styles.statTitle}>{title}</span>
      </div>
      <div className={styles.statValue}>{value}</div>
      <div className={styles.statFooter}>
        <span className={styles.trendUp}>
          <TrendingUp size={14} className="mr-1" />
          {trend}
        </span>
      </div>
    </div>
  );
}
