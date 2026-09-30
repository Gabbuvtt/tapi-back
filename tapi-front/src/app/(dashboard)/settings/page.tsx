'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Store, MapPin, Link as LinkIcon, Save } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import styles from './settings.module.css';

export default function SettingsPage() {
  const [storeData, setStoreData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [googleUrl, setGoogleUrl] = useState('');

  useEffect(() => {
    async function loadData() {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const { data } = await supabase
        .from('stores')
        .select('*')
        .eq('owner_email', session.user.email)
        .single();
        
      if (data) {
        setStoreData(data);
        setName(data.name || '');
        setAddress('Av. Principal 123, Centro'); // Placeholder, since it's not in DB yet
        setGoogleUrl(data.google_review_url || '');
      }
      setIsLoading(false);
    }
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      const { error } = await supabase
        .from('stores')
        .update({
          name: name,
          google_review_url: googleUrl
        })
        .eq('id', storeData.id);

      if (error) throw error;
      
      alert('¡Ajustes guardados con éxito!');
      window.location.reload(); // Para que el Topbar se actualice
    } catch (err) {
      console.error(err);
      alert('Error al guardar los ajustes.');
    }
    
    setIsSaving(false);
  };

  if (isLoading) return <div>Cargando ajustes...</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Ajustes del Negocio</h1>
        <p className={styles.subtitle}>Configura la información pública de tu comercio</p>
      </div>

      <div className={styles.card}>
        <div className={styles.logoSection}>
          <div className={styles.logoPlaceholder}>
            <Store size={32} />
          </div>
          <div>
            <h3 className={styles.logoTitle}>Logo del Comercio</h3>
            <p className={styles.logoSubtitle}>Recomendado: 512x512px. JPG o PNG.</p>
            <Button variant="outline" size="sm">Subir Imagen</Button>
          </div>
        </div>

        <form className="space-y-6" onSubmit={handleSave}>
          <div className={styles.formGrid}>
            <div>
              <label className={styles.label}>Nombre del Negocio</label>
              <input 
                type="text" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                className={styles.input} 
              />
            </div>
            <div>
              <label className={styles.label}>Categoría</label>
              <select className={styles.select}>
                <option>Cafetería</option>
                <option>Restaurante</option>
                <option>Bar</option>
              </select>
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}><MapPin size={16}/> Dirección Física</label>
            <input 
              type="text" 
              value={address} 
              onChange={e => setAddress(e.target.value)} 
              className={styles.input} 
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}><LinkIcon size={16}/> Link de Google Maps</label>
            <input 
              type="url" 
              value={googleUrl} 
              onChange={e => setGoogleUrl(e.target.value)} 
              className={styles.input} 
            />
            <p className={styles.hint}>Este link se utilizará para redirigir a los clientes a dejar reseñas 5 estrellas.</p>
          </div>
          
          <hr className={styles.divider} />
          
          <div className={styles.actions}>
            <Button type="submit" leftIcon={<Save size={18} />} isLoading={isSaving}>Guardar Cambios</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
