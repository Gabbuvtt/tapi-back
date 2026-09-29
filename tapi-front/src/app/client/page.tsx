'use client';

import React, { useEffect, useState } from 'react';
import { Coffee, Star, MapPin, MenuSquare, Gift } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './client.module.css';

export default function ClientViewPage() {
  const [stamps, setStamps] = useState(0);
  const [totalRequired, setTotalRequired] = useState(10);
  const [shopName, setShopName] = useState('Cargando...');
  const [isLoading, setIsLoading] = useState(true);

  // Estados para las reseñas
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [isReviewSubmitted, setIsReviewSubmitted] = useState(false);

  const handleRatingClick = (selectedRating: number) => {
    setRating(selectedRating);
    // Si son 4 o 5 estrellas, lo mandamos a Google Maps directo
    if (selectedRating >= 4) {
      window.open('https://g.page/r/tapi-example/review', '_blank');
      setIsReviewSubmitted(true);
    }
  };

  const submitInternalFeedback = () => {
    // Aquí iría el guardado en base de datos para que lo vea el dueño
    console.log("Feedback interno guardado:", feedbackText, "Estrellas:", rating);
    setIsReviewSubmitted(true);
  };

  useEffect(() => {
    async function fetchData() {
      // Por ahora para el MVP, buscamos la tarjeta específica que insertamos en el SQL
      const { data: cardData, error: cardError } = await supabase
        .from('loyalty_cards')
        .select(`
          stamps_count,
          total_required,
          stores ( name )
        `)
        .limit(1)
        .single();

      if (cardData) {
        setStamps(cardData.stamps_count);
        setTotalRequired(cardData.total_required);
        // @ts-ignore (Supabase nested type definition workaround)
        setShopName(cardData.stores?.name || 'TAPI Shop');
      }
      setIsLoading(false);
    }
    fetchData();
  }, []);

  const currentStamps = stamps;
  const remaining = totalRequired - currentStamps;

  return (
    <div className={styles.container}>
      <div className={styles.mobileWrapper}>
        
        {/* Header / Cover Image */}
        <div className={styles.headerImage}>
          <h1 className={styles.shopName}>{shopName}</h1>
          <p className={styles.greeting}>¡Hola, Liz! 👋</p>
        </div>

        <div className={styles.content}>
          
          {/* Loyalty Card Section */}
          <div className={styles.cardSection}>
            <div className={styles.cardTitle}>
              Mi Tarjeta
              <span className={styles.cardBadge}>Nivel Oro</span>
            </div>
            
            <div className={styles.loyaltyCard}>
              <div className={styles.cardGlow}></div>
              
              <div className="relative z-10 flex items-center gap-2 mb-2">
                <Coffee className="text-[var(--color-secondary)]" size={24} />
                <span className="text-white font-bold text-lg tracking-tight">El Aroma Club</span>
              </div>

              <div className={styles.stampGrid}>
                {Array.from({ length: totalRequired }).map((_, index) => {
                  const isDone = index < currentStamps;
                  const isGift = index === totalRequired - 1;
                  
                  return (
                    <div key={index} className={`${styles.stamp} ${isDone ? styles.stampDone : styles.stampPending}`}>
                      {isDone ? (
                        <Coffee size={16} />
                      ) : isGift ? (
                        <Gift size={16} />
                      ) : (
                        <span>{index + 1}</span>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className={styles.cardFooter}>
                <div className={styles.progressText}>
                  Estás a <span>{remaining} cafés</span> de tu bebida gratis.
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <a href="#" className={styles.menuBtn}>
            <MenuSquare size={18} />
            Ver Menú Digital
          </a>

          {/* Review Gating Section */}
          <div className={styles.reviewCard}>
            {!isReviewSubmitted ? (
              <>
                <h3 className={styles.reviewTitle}>¿Cómo calificarías tu visita?</h3>
                <div className="flex gap-2 my-2 justify-center">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => handleRatingClick(star)}
                      className="transition-transform hover:scale-110 focus:outline-none"
                      style={{ color: star <= rating ? '#FBBC05' : 'rgba(255, 255, 255, 0.2)' }}
                    >
                      <Star size={32} fill={star <= rating ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.5} />
                    </button>
                  ))}
                </div>

                {rating > 0 && rating <= 3 && (
                  <div className="w-full mt-4 flex flex-col gap-3 animate-in fade-in slide-in-from-top-2">
                    <p className={styles.reviewDesc}>
                      Lamentamos que tu experiencia no haya sido perfecta. ¿Qué podemos mejorar?
                    </p>
                    <textarea 
                      className="w-full bg-[rgba(0,0,0,0.2)] border border-[rgba(255,255,255,0.1)] rounded-lg p-3 text-white text-sm focus:outline-none focus:border-[var(--color-secondary)] min-h-[80px]"
                      placeholder="Cuéntanos tu experiencia..."
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                    />
                    <button 
                      onClick={submitInternalFeedback}
                      className="bg-[rgba(255,255,255,0.1)] text-white w-full py-3 rounded-lg font-semibold hover:bg-[rgba(255,255,255,0.15)] transition-colors"
                    >
                      Enviar Sugerencia
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="py-4 text-center animate-in fade-in zoom-in">
                <div className="w-12 h-12 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Star fill="currentColor" size={24} />
                </div>
                <h3 className={styles.reviewTitle}>¡Gracias por tu reseña!</h3>
                <p className={styles.reviewDesc}>Tu opinión nos ayuda muchísimo a mejorar.</p>
              </div>
            )}
          </div>

          {/* Footer Branding */}
          <div className={styles.footer}>
            <span className={styles.poweredBy}>Powered by</span>
            <img src="/tapi-logo-corto.png" alt="TAPI Logo" className={styles.footerLogo} />
          </div>

        </div>
      </div>
    </div>
  );
}
