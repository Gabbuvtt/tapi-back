'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, ChevronDown } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { supabase } from '@/lib/supabase';
import styles from './dashboard.module.css';

// Mock Data para el gráfico (hasta que se implemente tracking de taps por fecha)
const chartData = [
  { name: '1', scans: 12 }, { name: '2', scans: 19 }, { name: '3', scans: 15 },
  { name: '4', scans: 22 }, { name: '5', scans: 25 }, { name: '6', scans: 18 },
  { name: '7', scans: 45 }, { name: '8', scans: 32 }, { name: '9', scans: 56 },
  { name: '10', scans: 48 }, { name: '11', scans: 60 }, { name: '12', scans: 89 },
  { name: '13', scans: 95 }, { name: '14', scans: 112 }, { name: '15', scans: 130 },
];

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalTaps: 0,
    customers: 0,
  });
  
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

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
        // Fetch loyalty cards para sumar todos los sellos (Taps Totales)
        const { data: cards } = await supabase
          .from('loyalty_cards')
          .select('stamps_count, customers(full_name)')
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
        
        setStats({
          totalTaps: taps,
          customers: cards ? cards.length : 0
        });
        setRecentActivity(activityList.slice(0, 5)); // Últimos 5
      }
    }
    loadDashboard();
  }, []);

  return (
    <>
      <div className={styles.pageHeader}>
        <h1 className={styles.title}>Overview</h1>
        <div className={styles.filters}>
          <div className={styles.selectWrapper}>
            <select className={styles.select}>
              <option>Últimos 30 días</option>
              <option>Esta semana</option>
              <option>Este mes</option>
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
          value="4.9" 
          trend="Próximamente" 
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
                <Area 
                  type="monotone" 
                  dataKey="scans" 
                  stroke="var(--color-primary)" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorScans)" 
                />
              </AreaChart>
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
