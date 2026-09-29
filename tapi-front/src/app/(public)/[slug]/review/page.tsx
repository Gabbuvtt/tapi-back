'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Coffee, Info, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { StarRating } from '@/components/ui/StarRating';
import styles from './review.module.css';

export default function ReviewPage({ params }: { params: { slug: string } }) {
  const router = useRouter();
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) return;
    
    setIsSubmitting(true);
    // Simular llamada a API
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
      
      // Si el rating es >= 4, redirigir a Google en la vida real
      if (rating >= 4) {
        console.log("Redirigiendo a Google Maps...");
      }
    }, 1000);
  };

  if (isSuccess) {
    return (
      <div className={styles.container}>
        <div className={styles.successCard}>
          <CheckCircle2 size={64} className="text-[#16A34A]" />
          <h2 className="text-2xl font-bold text-[#1B3A5C]">¡Gracias por tu reseña!</h2>
          <p className="text-gray-600 mb-4">
            {rating >= 4 
              ? "Tu opinión es muy importante para nosotros. Por favor, compártela en Google."
              : "Agradecemos tu feedback. Trabajaremos para mejorar."}
          </p>
          <Button fullWidth onClick={() => router.push(`/${params.slug}`)}>
            Volver
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <nav className={styles.topNav}>
        <button className={styles.backBtn} onClick={() => router.back()}>
          <ArrowLeft size={24} />
        </button>
        <h1 className={styles.pageTitle}>Deja tu opinión</h1>
      </nav>

      <div className={styles.card}>
        <div className={styles.businessLogo}>
          <Coffee size={24} />
        </div>
        <div className={styles.businessName}>Café El Aroma</div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.ratingSection}>
            <StarRating 
              rating={rating} 
              onChange={setRating} 
              size={48} 
            />
            <div className={styles.ratingLabel}>
              {rating === 0 ? 'Toca para calificar' : 'Tu opinión nos ayuda a mejorar'}
            </div>
          </div>

          <textarea
            className={styles.textarea}
            placeholder="Cuéntanos tu experiencia (opcional)..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />

          {rating >= 4 && (
            <div className={styles.infoNote}>
              <Info size={20} className="shrink-0" />
              <span>Las reseñas de 4 o más estrellas se publicarán en nuestro perfil de Google Maps.</span>
            </div>
          )}

          <Button 
            type="submit" 
            fullWidth 
            size="lg" 
            disabled={rating === 0}
            isLoading={isSubmitting}
          >
            Enviar Reseña
          </Button>
        </form>
      </div>
    </div>
  );
}
