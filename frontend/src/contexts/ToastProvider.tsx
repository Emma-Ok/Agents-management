// Provider para notificaciones Toast
'use client';

import React from 'react';
import { Toaster } from 'react-hot-toast';

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        // Configuración por defecto
        duration: 4000,
        style: {
          background: '#ffffff',
          color: '#374151',
          fontSize: '14px',
          borderRadius: '8px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          border: '1px solid #e5e7eb',
        },
        // Configuración por tipo
        success: {
          iconTheme: {
            primary: '#10b981',
            secondary: '#ffffff',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#ffffff',
          },
          duration: 6000,
        },
        loading: {
          iconTheme: {
            primary: '#6b7280',
            secondary: '#ffffff',
          },
        },
      }}
    />
  );
}
