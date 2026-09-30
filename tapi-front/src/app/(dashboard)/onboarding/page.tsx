'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/Button';
import { Store, MapPin, Coffee, Palette, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import styles from './onboarding.module.css';

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isSaving, setIsSaving] = useState(false);
  const [storeId, setStoreId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    google_review_url: '',
    primary_color: '#E88B2E',
    stamps_required: 10,
    reward_title: '1 Producto Gratis'
  });

  useEffect(() => {
    async function loadStore() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data } = await supabase
        .from('stores')
        .select('id, name, slug')
        .eq('owner_email', session.user.email)
        .single();
        
      if (data) {
        setStoreId(data.id);
        setFormData(prev => ({ ...prev, name: data.name, slug: data.slug }));
      }
    }
    loadStore();
  }, []);

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await supabase.from('stores').update({
        name: formData.name,
        google_review_url: formData.google_review_url,
        primary_color: formData.primary_color,
        is_onboarded: true
      }).eq('id', storeId);

      await supabase.from('loyalty_programs').upsert({
        store_id: storeId,
        stamps_required: formData.stamps_required,
        reward_title: formData.reward_title
      }, { onConflict: 'store_id' });

      window.location.href = '/dashboard'; // Force full reload to rebuild layout state
    } catch (err) {
      console.error(err);
      alert('Error guardando configuración');
      setIsSaving(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.wizardCard}>
        
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.stepIndicator}>Paso {step} de 3</div>
          <h1 className={styles.title}>
            {step === 1 && 'Personaliza tu Negocio'}
            {step === 2 && 'Reglas de Fidelidad'}
            {step === 3 && 'Conecta Google Maps'}
          </h1>
          <p className={styles.subtitle}>
            {step === 1 && 'Dale color y vida a la tarjeta que verán tus clientes.'}
            {step === 2 && '¿Cuántos sellos necesitan para ganar y cuál es el premio?'}
            {step === 3 && 'Cobra reseñas automáticas cuando tengan experiencias de 5 estrellas.'}
          </p>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {step === 1 && (
            <div className={styles.formGroup}>
              <div className={styles.inputBox}>
                <label><Store size={16} /> Nombre de la Tienda</label>
                <input 
                  type="text" 
                  value={formData.name} 
                  onChange={(e) => setFormData({...formData, name: e.target.value})} 
                  className={styles.input} 
                />
              </div>
              <div className={styles.inputBox}>
                <label><Palette size={16} /> Color Principal de la Marca</label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input 
                    type="color" 
                    value={formData.primary_color}
                    onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                    className={styles.colorPicker}
                  />
                  <input 
                    type="text" 
                    value={formData.primary_color}
                    onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                    className={styles.input}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className={styles.formGroup}>
              <div className={styles.inputBox}>
                <label><Coffee size={16} /> Número de Sellos para Ganar</label>
                <select 
                  value={formData.stamps_required}
                  onChange={(e) => setFormData({...formData, stamps_required: Number(e.target.value)})}
                  className={styles.select}
                >
                  <option value={5}>5 Sellos</option>
                  <option value={8}>8 Sellos</option>
                  <option value={10}>10 Sellos</option>
                  <option value={12}>12 Sellos</option>
                </select>
              </div>
              <div className={styles.inputBox}>
                <label><CheckCircle size={16} /> ¿Cuál es el Premio Final?</label>
                <input 
                  type="text" 
                  placeholder="Ej: 1 Bebida Gratis"
                  value={formData.reward_title}
                  onChange={(e) => setFormData({...formData, reward_title: e.target.value})}
                  className={styles.input}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className={styles.formGroup}>
              <div className={styles.inputBox}>
                <label><MapPin size={16} /> URL de Reseñas de Google Maps</label>
                <input 
                  type="url" 
                  placeholder="https://g.page/r/tu-negocio/review"
                  value={formData.google_review_url}
                  onChange={(e) => setFormData({...formData, google_review_url: e.target.value})}
                  className={styles.input}
                />
                <p className={styles.hint}>Los clientes que te den 4 o 5 estrellas en TAPI serán redirigidos aquí.</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer / Actions */}
        <div className={styles.footer}>
          {step > 1 ? (
            <Button variant="outline" leftIcon={<ArrowLeft size={16} />} onClick={handlePrev}>
              Atrás
            </Button>
          ) : <div></div>}
          
          {step < 3 ? (
            <Button rightIcon={<ArrowRight size={16} />} onClick={handleNext}>
              Siguiente
            </Button>
          ) : (
            <Button rightIcon={<CheckCircle size={16} />} onClick={handleSave} isLoading={isSaving}>
              ¡Terminar y Entrar!
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
