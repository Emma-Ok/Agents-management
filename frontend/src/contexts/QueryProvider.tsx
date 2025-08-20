// Provider de React Query para manejo de estado global
'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Configuración del cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache por 5 minutos
      staleTime: 5 * 60 * 1000,
      // Reintento fallido después de 3 intentos
      retry: 3,
      // Refetch en window focus solo en producción
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
    },
    mutations: {
      // Reintento de mutaciones una vez
      retry: 1,
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// Hook para acceder al query client
export { queryClient };
