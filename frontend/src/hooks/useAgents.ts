// Hook personalizado para manejar operaciones con agentes - USANDO REACT QUERY + AXIOS

import { 
  useAgents, 
  useAgentsQuery, 
  useAgentQuery,
  useCreateAgentMutation,
  useUpdateAgentMutation,
  useDeleteAgentMutation,
  QUERY_KEYS 
} from './useAgentsQuery';

// Re-exportar hooks de React Query para compatibilidad
export { 
  useAgents, 
  useAgentsQuery, 
  useAgentQuery,
  useCreateAgentMutation,
  useUpdateAgentMutation,
  useDeleteAgentMutation,
  QUERY_KEYS 
};

// Hook de compatibilidad para agente individual
export function useAgent(id: string) {
  const query = useAgentQuery(id);
  
  return {
    agent: query.data,
    loading: { 
      isLoading: query.isLoading, 
      error: query.error?.message || null 
    },
    refetch: query.refetch,
  };
}

// Hook legado para compatibilidad (deprecated)
export function useAgentsLegacy() {
  console.warn('useAgentsLegacy is deprecated. Use useAgents from useAgentsQuery instead.');
  return useAgents();
}
