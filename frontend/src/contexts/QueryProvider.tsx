// Provider de React Query para manejo de estado global
'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

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
      {/* DevTools solo en desarrollo - temporalmente comentado */}
      {/* {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false} 
          position="bottom-right"
        />
      )} */}
    </QueryClientProvider>
  );
}

// Hook para acceder al query client
export { queryClient };
