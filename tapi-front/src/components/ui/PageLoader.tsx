import React from 'react';
import { Loader2 } from 'lucide-react';
import styles from './PageLoader.module.css';

interface PageLoaderProps {
  text?: string;
}

export default function PageLoader({ text = 'Cargando...' }: PageLoaderProps) {
  return (
    <div className={styles.container}>
      <div className={styles.spinnerWrapper}>
         <Loader2 size={32} className={styles.spinner} />
      </div>
      <p className={styles.text}>{text}</p>
    </div>
  );
}
