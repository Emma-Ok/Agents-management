// Hook personalizado usando React Query para manejar agentes
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/apiAxios';
import { Agent, CreateAgentDTO, UpdateAgentDTO } from '@/types';
import toast from 'react-hot-toast';

// Query Keys
export const QUERY_KEYS = {
  agents: ['agents'] as const,
  agent: (id: string) => ['agents', id] as const,
  agentDocuments: (agentId: string) => ['agents', agentId, 'documents'] as const,
};

// Hook para listar todos los agentes
export function useAgentsQuery() {
  return useQuery({
    queryKey: QUERY_KEYS.agents,
    queryFn: () => apiService.getAgents(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    retry: 3,
    meta: {
      errorMessage: 'Error al cargar la lista de agentes',
    },
  });
}

// Hook para obtener un agente específico
export function useAgentQuery(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.agent(id),
    queryFn: () => apiService.getAgent(id),
    enabled: !!id, // Solo ejecutar si hay ID
    staleTime: 5 * 60 * 1000,
    retry: 3,
    meta: {
      errorMessage: `Error al cargar el agente ${id}`,
    },
  });
}

// Hook para crear agente
export function useCreateAgentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateAgentDTO) => apiService.createAgent(data),
    onSuccess: (newAgent) => {
      // Invalidar cache para forzar refetch
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.agents });

      toast.success(`Agente "${newAgent.name}" creado exitosamente`);
    },
    onError: (error: Error) => {
      toast.error(`Error al crear agente: ${error.message}`);
    },
  });
}

// Hook para actualizar agente
export function useUpdateAgentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateAgentDTO }) => 
      apiService.updateAgent(id, data),
    onSuccess: (updatedAgent, { id }) => {
      // Actualizar cache del agente específico
      queryClient.setQueryData(QUERY_KEYS.agent(id), updatedAgent);
      
      // Actualizar lista de agentes
      queryClient.setQueryData(QUERY_KEYS.agents, (oldData: { agents: Agent[]; total: number } | undefined) => {
        if (oldData?.agents) {
          return {
            ...oldData,
            agents: oldData.agents.map((agent: Agent) => 
              agent.id === id ? updatedAgent : agent
            ),
          };
        }
        return oldData;
      });

      // No enviamos toast aquí - se maneja en useAgentOperationNotifications
    },
    onError: () => {
      // No enviamos toast aquí - se maneja en useAgentOperationNotifications
    },
  });
}

// Hook para eliminar agente
export function useDeleteAgentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiService.deleteAgent(id),
    onSuccess: (_, deletedId) => {
      // Remover del cache
      queryClient.removeQueries({ queryKey: QUERY_KEYS.agent(deletedId) });
      
      // Invalidar todo el cache de agentes para hacer refetch completo
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.agents });

      toast.success('Agente eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(`Error al eliminar agente: ${error.message}`);
    },
  });
}

// Hook combinado para facilitar el uso
export function useAgents() {
  const agentsQuery = useAgentsQuery();
  const createMutation = useCreateAgentMutation();
  const updateMutation = useUpdateAgentMutation();
  const deleteMutation = useDeleteAgentMutation();

  return {
    // Data
    agents: agentsQuery.data?.agents?.filter(agent => agent && agent.id) || [],
    total: agentsQuery.data?.total || 0,
    
    // Loading states
    isLoading: agentsQuery.isLoading,
    isError: agentsQuery.isError,
    error: agentsQuery.error,
    
    // Actions
    createAgent: (data: CreateAgentDTO) => {
      return new Promise<Agent>((resolve, reject) => {
        createMutation.mutate(data, {
          onSuccess: (newAgent) => resolve(newAgent),
          onError: (error) => reject(error)
        });
      });
    },
    updateAgent: (id: string, data: UpdateAgentDTO) => 
      updateMutation.mutate({ id, data }),
    deleteAgent: deleteMutation.mutate,
    
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    
    // Utilities
    refetch: agentsQuery.refetch,
  };
}
