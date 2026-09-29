'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { Store, MapPin, Link as LinkIcon, Save } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-[var(--color-primary)] mb-1 tracking-tight">Ajustes del Negocio</h1>
        <p className="text-gray-500">Configura la información pública de tu comercio</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="flex items-center gap-6 mb-8">
          <div className="w-24 h-24 rounded-full bg-gray-100 flex items-center justify-center border-2 border-dashed border-gray-300 text-gray-400 cursor-pointer hover:bg-gray-50">
            <Store size={32} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-1">Logo del Comercio</h3>
            <p className="text-sm text-gray-500 mb-3">Recomendado: 512x512px. JPG o PNG.</p>
            <Button variant="outline" size="sm">Subir Imagen</Button>
          </div>
        </div>

        <form className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nombre del Negocio</label>
              <input type="text" defaultValue="Café El Aroma" className="w-full h-11 px-4 rounded-lg border border-gray-200 focus:outline-none focus:border-[var(--color-secondary)] focus:ring-1 focus:ring-[var(--color-secondary)]" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categoría</label>
              <select className="w-full h-11 px-4 rounded-lg border border-gray-200 focus:outline-none focus:border-[var(--color-secondary)]">
                <option>Cafetería</option>
                <option>Restaurante</option>
                <option>Bar</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2"><MapPin size={16}/> Dirección Física</label>
            <input type="text" defaultValue="Av. Principal 123, Centro" className="w-full h-11 px-4 rounded-lg border border-gray-200 focus:outline-none focus:border-[var(--color-secondary)]" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2"><LinkIcon size={16}/> Link de Google Maps</label>
            <input type="url" defaultValue="https://maps.google.com/..." className="w-full h-11 px-4 rounded-lg border border-gray-200 focus:outline-none focus:border-[var(--color-secondary)] text-blue-600" />
            <p className="text-xs text-gray-500 mt-2">Este link se utilizará para redirigir a los clientes a dejar reseñas 5 estrellas.</p>
          </div>
          
          <hr className="border-gray-100 my-8" />
          
          <div className="flex justify-end">
            <Button leftIcon={<Save size={18} />}>Guardar Cambios</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
