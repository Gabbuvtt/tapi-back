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
  const [logoUrl, setLogoUrl] = useState('');

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
        setLogoUrl(data.logo_url || '');
      }
      setIsLoading(false);
    }
    loadData();
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        // Redimensionar para no sobrecargar la base de datos (Max 512x512)
        const canvas = document.createElement('canvas');
        const MAX_SIZE = 512;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > MAX_SIZE) {
            height *= MAX_SIZE / width;
            width = MAX_SIZE;
          }
        } else {
          if (height > MAX_SIZE) {
            width *= MAX_SIZE / height;
            height = MAX_SIZE;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0, width, height);
        
        // Convertir a Base64 (webp es más ligero)
        const base64String = canvas.toDataURL('image/webp', 0.8);
        setLogoUrl(base64String);
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      const { error } = await supabase
        .from('stores')
        .update({
          name: name,
          google_review_url: googleUrl,
          logo_url: logoUrl
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
          <div className={styles.logoPlaceholder} style={{ overflow: 'hidden' }}>
            {logoUrl ? (
              <img src={logoUrl} alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <Store size={32} />
            )}
          </div>
          <div style={{ flex: 1 }}>
            <h3 className={styles.logoTitle}>Logo del Comercio</h3>
            <p className={styles.logoSubtitle} style={{ marginBottom: '12px' }}>Sube el logo de tu marca desde tu computadora.</p>
            
            <label className={styles.actionBtn} style={{ padding: '8px 16px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '6px', cursor: 'pointer', display: 'inline-block', fontSize: '14px', fontWeight: 500 }}>
              Seleccionar Imagen
              <input 
                type="file" 
                accept="image/*" 
                style={{ display: 'none' }} 
                onChange={handleImageUpload}
                onClick={(e) => { (e.target as HTMLInputElement).value = ''; }}
              />
            </label>
            {logoUrl && <button type="button" onClick={() => setLogoUrl('')} style={{ marginLeft: '12px', fontSize: '14px', color: 'var(--color-error)', background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, textDecoration: 'underline' }}>Eliminar</button>}
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
