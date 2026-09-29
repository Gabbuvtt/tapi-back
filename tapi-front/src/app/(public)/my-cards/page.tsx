'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Coffee } from 'lucide-react';
import styles from './cards.module.css';

export default function MyCardsPage() {
  const router = useRouter();
  const [progress, setProgress] = useState(0);

  // Animación del progreso circular
  useEffect(() => {
    const timer = setTimeout(() => setProgress(7), 300);
    return () => clearTimeout(timer);
  }, []);

  const totalVisits = 10;
  const percentage = (progress / totalVisits) * 100;
  const radius = 76;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className={styles.container}>
      <nav className={styles.topNav}>
        <button className={styles.backBtn} onClick={() => router.push('/')}>
          <ArrowLeft size={24} />
        </button>
        <h1 className={styles.pageTitle}>Mi Tarjeta de Lealtad</h1>
      </nav>

      <div className={styles.content}>
        <div className={styles.loyaltyCard}>
          <div className={styles.businessHeader}>
            <div className={styles.businessLogo}>
              <Coffee size={24} />
            </div>
            <div>
              <div className={styles.businessName}>Café El Aroma</div>
              <div className={styles.category}>Cafetería</div>
            </div>
          </div>

          <div className={styles.progressContainer}>
            <svg className={styles.progressRing}>
              <circle
                className={styles.progressTrack}
                cx="90" cy="90" r={radius}
              />
              <circle
                className={styles.progressFill}
                cx="90" cy="90" r={radius}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
              />
            </svg>
            <div className={styles.progressText}>
              <div className={styles.progressValue}>{progress}</div>
              <div className={styles.progressLabel}>/ {totalVisits} visitas</div>
            </div>
          </div>

          <div className={styles.badge}>ACTIVA</div>

          <div className={styles.statsRow}>
            <div className={styles.statCol}>
              <div className={styles.statNum}>23</div>
              <div className={styles.statName}>Visitas Totales</div>
            </div>
            <div className={styles.statCol}>
              <div className={styles.statNum}>Sep '26</div>
              <div className={styles.statName}>Miembro Desde</div>
            </div>
          </div>
        </div>

        <div>
          <h3 className={styles.sectionTitle}>Rewards Disponibles</h3>
          
          <div className="flex flex-col gap-3 mt-4">
            <div className={styles.rewardCard}>
              <div className={styles.rewardInfo}>
                <h4>10% Descuento</h4>
                <p>Canjeable con 10 visitas</p>
              </div>
              <button className={styles.btnRedeem}>Canjear</button>
            </div>

            <div className={styles.rewardCard}>
              <div className={styles.rewardInfo}>
                <h4>Café Gratis</h4>
                <p>Necesitas 3 visitas más</p>
              </div>
              <button className={`${styles.btnRedeem} ${styles.btnDisabled}`} disabled>
                Bloqueado
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
