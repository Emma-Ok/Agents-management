// Hook personalizado para manejar operaciones con agentes - USANDO AXIOS

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '@/services/apiAxios';
import { Agent, CreateAgentDTO, UpdateAgentDTO, LoadingState } from '@/types';

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<LoadingState>({ isLoading: true });

  // Cargar todos los agentes
  const fetchAgents = useCallback(async () => {
    try {
      setLoading({ isLoading: true });
      const { agents: agentsList } = await apiService.getAgents();
      setAgents(agentsList);
      setLoading({ isLoading: false });
    } catch (error) {
      setLoading({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Error al cargar agentes' 
      });
    }
  }, []);

  // Crear un nuevo agente
  const createAgent = useCallback(async (data: CreateAgentDTO): Promise<Agent> => {
    try {
      const newAgent = await apiService.createAgent(data);
      setAgents(prev => [newAgent, ...prev]);
      return newAgent;
    } catch (error) {
      throw error instanceof Error ? error : new Error('Error al crear agente');
    }
  }, []);

  // Actualizar un agente
  const updateAgent = useCallback(async (id: string, data: UpdateAgentDTO): Promise<Agent> => {
    try {
      const updatedAgent = await apiService.updateAgent(id, data);
      setAgents(prev => prev.map(agent => 
        agent.id === id ? updatedAgent : agent
      ));
      return updatedAgent;
    } catch (error) {
      throw error instanceof Error ? error : new Error('Error al actualizar agente');
    }
  }, []);

  // Eliminar un agente
  const deleteAgent = useCallback(async (id: string): Promise<void> => {
    try {
      await apiService.deleteAgent(id);
      setAgents(prev => prev.filter(agent => agent.id !== id));
    } catch (error) {
      throw error instanceof Error ? error : new Error('Error al eliminar agente');
    }
  }, []);

  // Cargar agentes al montar el hook
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return {
    agents,
    loading,
    createAgent,
    updateAgent,
    deleteAgent,
    refetch: fetchAgents,
  };
}

export function useAgent(id: string) {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState<LoadingState>({ isLoading: true });

  const fetchAgent = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading({ isLoading: true });
      const agentData = await apiService.getAgent(id);
      setAgent(agentData);
      setLoading({ isLoading: false });
    } catch (error) {
      setLoading({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Error al cargar agente' 
      });
    }
  }, [id]);

  useEffect(() => {
    fetchAgent();
  }, [fetchAgent]);

  return {
    agent,
    loading,
    refetch: fetchAgent,
  };
}
