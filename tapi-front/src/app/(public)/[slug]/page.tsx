'use client';

import React, { useEffect, useState } from 'react';
import { Coffee, MenuSquare, MessageSquare, Gift, ArrowRight } from 'lucide-react';
import styles from './landing.module.css';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function NfcLandingPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [progress, setProgress] = useState(0);

  // Animación del progreso
  useEffect(() => {
    const timer = setTimeout(() => setProgress(7), 300);
    return () => clearTimeout(timer);
  }, []);

  const totalVisits = 10;
  const percentage = (progress / totalVisits) * 100;
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.logo}>
          <Coffee size={36} />
        </div>
        <h1 className={styles.businessName}>Café El Aroma</h1>
        <span className={styles.category}>Cafetería</span>
      </div>

      <div className={styles.card}>
        <div className={styles.progressRingContainer}>
          <svg className={styles.progressRing}>
            <circle
              className={styles.progressTrack}
              cx="80" cy="80" r={radius}
            />
            <circle
              className={styles.progressFill}
              cx="80" cy="80" r={radius}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            />
          </svg>
          <div className={styles.progressText}>
            <div className={styles.progressValue}>{progress}</div>
            <div className={styles.progressLabel}>/ {totalVisits} visitas</div>
          </div>
        </div>

        <p className={styles.message}>
          ¡Te faltan {totalVisits - progress} visitas para tu café gratis!
        </p>

        <div className={styles.actionsGrid}>
          <Link href={`/${slug}/menu`} className={styles.actionBtn}>
            <MenuSquare size={24} className="text-[#1B3A5C]" />
            Ver Menú
          </Link>
          <Link href={`/${slug}/review`} className={styles.actionBtn}>
            <MessageSquare size={24} className="text-[#E88B2E]" />
            Reseña
          </Link>
          <Link href="/my-cards" className={styles.actionBtn}>
            <Gift size={24} className="text-[#16A34A]" />
            Rewards
          </Link>
        </div>
      </div>

      <div className={styles.rewardCard}>
        <div className={styles.rewardInfo}>
          <h4>10% de Descuento</h4>
          <p>Disponible para canjear ahora</p>
        </div>
        <div className="bg-white/20 p-2 rounded-full">
          <ArrowRight size={20} />
        </div>
      </div>
    </div>
  );
}
