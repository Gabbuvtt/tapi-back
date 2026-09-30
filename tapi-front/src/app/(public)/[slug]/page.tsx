'use client';

import React, { useEffect, useState } from 'react';
import { Coffee, Star, MapPin, MenuSquare, Gift } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './client.module.css';

export default function ClientViewPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = React.use(params);
  const [user, setUser] = useState<any>(null);
  const [customerData, setCustomerData] = useState<any>(null);
  const [phoneInput, setPhoneInput] = useState('');
  const [stamps, setStamps] = useState(0);
  const [totalRequired, setTotalRequired] = useState(10);
  const [shopName, setShopName] = useState('Cargando...');
  const [isLoading, setIsLoading] = useState(true);
  
  // Estados para el Menú
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [menuItems, setMenuItems] = useState<any[]>([]);

  // Estados para las reseñas
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [isReviewSubmitted, setIsReviewSubmitted] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  const handleRatingClick = (selectedRating: number) => {
    if (!isReviewSubmitted) setRating(selectedRating);
  };

  const submitFeedback = async () => {
    if (rating === 0 || isSubmittingReview) return; 

    setIsSubmittingReview(true);
    
    try {
      // 1. Insert into Supabase 'reviews' table
      const status = rating >= 4 ? 'Google' : 'Interna';
      
      const { data: storeInfo } = await supabase
        .from('stores')
        .select('id, google_review_url')
        .eq('slug', slug)
        .single();
        
      if (storeInfo) {
        await supabase.from('reviews').insert({
          store_id: storeInfo.id,
          customer_id: customerData?.id || null, // works even if anonymous
          rating: rating,
          comment: feedbackText,
          status: status
        });
        
        // 2. Filtro inteligente (Review Gating)
        if (rating >= 4 && storeInfo.google_review_url) {
          window.location.href = storeInfo.google_review_url;
        }
      }
      
      setIsReviewSubmitted(true);
    } catch (err) {
      console.error('Error guardando reseña', err);
      alert('Hubo un error al enviar tu reseña.');
    }
    
    setIsSubmittingReview(false);
  };

  useEffect(() => {
    async function init() {
      // 1. Traer datos de la tienda y la tarjeta basado en el SLUG
      const { data: cardData } = await supabase
        .from('stores')
        .select(`
          id,
          name,
          loyalty_programs ( stamps_required )
        `)
        .eq('slug', slug)
        .single();

      if (cardData) {
        setShopName(cardData.name);
        setTotalRequired(cardData.loyalty_programs?.[0]?.stamps_required || 10);
        
        // Cargar el Menú
        const { data: items } = await supabase
          .from('menu_items')
          .select('*, menu_categories!inner(store_id, name)')
          .eq('menu_categories.store_id', cardData.id);
        setMenuItems(items || []);
      }

      // 2. Revisar si hay sesión de Google activa
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.user) {
        setUser(session.user);
        
        // Intentar recuperar el customer existente por email sin hacer upsert
        const { data: customer } = await supabase
          .from('customers')
          .select('*')
          .eq('email', session.user.email)
          .single();
        
        setCustomerData(customer);
        
        // Consultar los sellos reales del cliente para esta tienda
        if (customer && cardData) {
          const { data: loyaltyCard } = await supabase
            .from('loyalty_cards')
            .select('current_stamps')
            .eq('customer_id', customer.id)
            .eq('store_id', cardData.id)
            .single();
            
          setStamps(loyaltyCard?.current_stamps || 0);
        }
      }
      setIsLoading(false);
    }
    init();
  }, [slug]);

  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.href }
    });
  };

  const savePhoneNumber = async () => {
    if (!phoneInput || phoneInput.length < 8) return;
    
    // Insertar el nuevo cliente en la BD
    const { data, error } = await supabase.from('customers').insert({
      auth_id: user.id,
      email: user.email,
      name: user.user_metadata?.full_name || 'Cliente',
      phone_number: phoneInput
    }).select().single();
      
    if (data) {
      setCustomerData(data);
    } else {
      console.error(error);
      alert('Error al guardar el teléfono. Es posible que este número ya esté registrado.');
    }
  };

  const currentStamps = stamps;
  const remaining = totalRequired - currentStamps;

  if (isLoading) {
    return <div className={styles.container}><div className={styles.mobileWrapper}></div></div>;
  }

  if (!user) {
    return (
      <div className={styles.container}>
        <div className={styles.mobileWrapper} style={{ justifyContent: 'center', padding: '24px' }}>
          <div className={styles.reviewCard} style={{ marginTop: 0, padding: '32px 24px' }}>
            <div style={{ marginBottom: '24px' }}>
              <Coffee className="text-[var(--color-secondary)] mx-auto mb-4" size={48} />
              <h2 style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                ¡Bienvenido a {shopName}!
              </h2>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px', lineHeight: 1.5 }}>
                Inicia sesión con Google en 1 segundo para reclamar tu sello y empezar a ganar recompensas.
              </p>
            </div>
            
            <button 
              onClick={handleGoogleLogin}
              className={styles.googleBtn}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continuar con Google
            </button>
          </div>
          
          <div className={styles.footer} style={{ marginTop: '40px' }}>
            <span className={styles.poweredBy}>Powered by</span>
            <img src="/tapi-logo-corto.png" alt="TAPI Logo" className={styles.footerLogo} />
          </div>
        </div>
      </div>
    );
  }

  if (user && (!customerData || !customerData.phone_number)) {
    return (
      <div className={styles.container}>
        <div className={styles.mobileWrapper} style={{ justifyContent: 'center', padding: '24px' }}>
          <div className={styles.reviewCard} style={{ marginTop: 0, padding: '32px 24px' }}>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                <span style={{ fontSize: '32px' }}>📱</span>
              </div>
              <h2 style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                ¡Último paso, {user.user_metadata?.full_name?.split(' ')[0]}!
              </h2>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px', lineHeight: 1.5 }}>
                ¿A qué número de WhatsApp te enviamos tus recompensas cuando las ganes?
              </p>
            </div>
            
            <input 
              type="tel"
              placeholder="+58 414 123 4567"
              value={phoneInput}
              onChange={(e) => setPhoneInput(e.target.value)}
              className={styles.feedbackTextarea}
              style={{ minHeight: '48px', marginBottom: '16px', textAlign: 'center', fontSize: '18px', fontWeight: 'bold', resize: 'none' }}
            />

            <button 
              onClick={savePhoneNumber}
              className={styles.submitBtn}
            >
              Guardar y ver mi tarjeta
            </button>
          </div>
          
          <div className={styles.footer} style={{ marginTop: '40px' }}>
            <span className={styles.poweredBy}>Powered by</span>
            <img src="/tapi-logo-corto.png" alt="TAPI Logo" className={styles.footerLogo} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.mobileWrapper}>
        
        {/* Header / Cover Image */}
        <div className={styles.headerImage}>
          <h1 className={styles.shopName}>{shopName}</h1>
          <p className={styles.greeting}>¡Hola, {user.user_metadata?.full_name?.split(' ')[0] || 'Liz'}! 👋</p>
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
              
              <div style={{ position: 'relative', zIndex: 10, display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                <Gift className="text-[var(--color-secondary)]" size={24} />
                <span style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', letterSpacing: '-0.02em' }}>{shopName} Rewards</span>
              </div>

              <div className={styles.stampGrid}>
                {Array.from({ length: totalRequired }).map((_, index) => {
                  const isDone = index < currentStamps;
                  const isGift = index === totalRequired - 1;
                  
                  return (
                    <div key={index} className={`${styles.stamp} ${isDone ? styles.stampDone : styles.stampPending}`}>
                      {isDone ? (
                        <Star size={16} />
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
                  Estás a <span>{remaining} visitas</span> de tu recompensa gratis.
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <button 
            onClick={(e) => { e.preventDefault(); setIsMenuOpen(true); }} 
            className={styles.menuBtn}
            style={{ cursor: 'pointer' }}
          >
            <MenuSquare size={18} />
            Ver Menú Digital
          </button>

          {/* Review Gating Section */}
          <div className={styles.reviewCard}>
            {!isReviewSubmitted ? (
              <>
                <h3 className={styles.reviewTitle}>¿Cómo calificarías tu visita?</h3>
                <div className={styles.interactiveStars}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <div
                      key={star}
                      onClick={() => handleRatingClick(star)}
                      className={styles.starWrapper}
                      style={{ color: star <= rating ? '#FBBC05' : 'rgba(255, 255, 255, 0.2)' }}
                    >
                      <Star size={36} fill={star <= rating ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.5} />
                    </div>
                  ))}
                </div>

                {rating > 0 && (
                  <div className={styles.feedbackContainer}>
                    <p className={styles.reviewDesc}>
                      {rating >= 4 
                        ? '¡Nos alegra mucho! ¿Quieres dejarnos un comentario adicional?'
                        : 'Lamentamos que tu experiencia no haya sido perfecta. ¿Qué podemos mejorar?'
                      }
                    </p>
                    <textarea 
                      className={styles.feedbackTextarea}
                      placeholder="Cuéntanos tu experiencia..."
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                    />
                    <button 
                      onClick={submitFeedback}
                      className={styles.submitBtn}
                    >
                      Enviar Valoración
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="py-4 text-center animate-in fade-in zoom-in">
                <div className="w-12 h-12 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Star fill="currentColor" size={24} />
                </div>
                <h3 className={styles.reviewTitle}>
                  {rating >= 4 ? '¡Gracias por tu reseña!' : '¡Gracias por ayudarnos a mejorar!'}
                </h3>
                <p className={styles.reviewDesc}>
                  Tu opinión es fundamental para nosotros.
                </p>
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

      {/* MODAL DEL MENÚ DIGITAL */}
      {isMenuOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 999, display: 'flex', justifyContent: 'center', alignItems: 'flex-end', animation: 'fadeIn 0.2s ease-in-out' }}>
          <div style={{ width: '100%', maxWidth: '480px', backgroundColor: 'var(--color-bg)', height: '85vh', borderTopLeftRadius: '24px', borderTopRightRadius: '24px', display: 'flex', flexDirection: 'column', overflow: 'hidden', animation: 'slideUp 0.3s ease-in-out' }}>
            <div style={{ padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>Menú de {shopName}</h2>
              <button onClick={() => setIsMenuOpen(false)} style={{ background: 'none', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' }}>&times;</button>
            </div>
            
            <div style={{ padding: '24px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {menuItems.length === 0 ? (
                <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', marginTop: '40px' }}>No hay productos disponibles por ahora.</p>
              ) : (
                menuItems.map(item => (
                  <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div>
                      <h4 style={{ color: 'white', fontWeight: 'bold', margin: 0 }}>{item.name}</h4>
                      <p style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginTop: '4px', marginBottom: '8px' }}>
                        {item.menu_categories?.name || 'General'}
                      </p>
                      {item.description && (
                        <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px', lineHeight: 1.4, margin: 0 }}>{item.description}</p>
                      )}
                    </div>
                    <div style={{ color: 'var(--color-secondary)', fontWeight: 'bold', fontSize: '16px', marginLeft: '16px' }}>
                      ${Number(item.price).toFixed(2)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          <style>{`
            @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          `}</style>
        </div>
      )}

    </div>
  );
}
