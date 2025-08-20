// Servicio de API con Axios - ADAPTADO AL BACKEND EXISTENTE

import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  Agent, 
  AgentListItem,
  AgentsListResponse,
  CreateAgentDTO, 
  UpdateAgentDTO, 
  Document, 
  UploadDocumentResponse,
  ApiError
} from '@/types';

// Configuración base de la API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Interceptor para logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Interceptor para respuestas
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status}`, response.data);
        return response;
      },
      (error: AxiosError) => {
        console.error('❌ Response Error:', error.response?.data || error.message);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): Error {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      return new Error('No se puede conectar al servidor. Verifica que el backend esté ejecutándose en http://localhost:8000');
    }
    
    const errorData = error.response?.data as ApiError;
    const message = errorData?.detail || errorData?.message || errorData?.error || error.message;
    
    return new Error(message);
  }

  // ====== AGENTES ======

  // Listar todos los agentes (adaptado al formato de tu backend)
  async getAgents(skip: number = 0, limit: number = 20): Promise<{ agents: Agent[]; total: number }> {
    try {
      // Tu backend devuelve: { items: [], total: number, skip: number, ... }
      const response = await this.client.get<AgentsListResponse>('/agents', {
        params: { skip, limit }
      });

      // Para mostrar los agentes en el frontend, necesitamos obtener los detalles de cada uno
      // ya que tu listAgents solo devuelve id, documents_count y created_at
      const agentPromises = response.data.items.map(item => this.getAgent(item.id));
      const agents = await Promise.all(agentPromises);

      return {
        agents: agents.filter(agent => agent !== null) as Agent[],
        total: response.data.total
      };
    } catch (error) {
      console.error('Error fetching agents:', error);
      throw error;
    }
  }

  // Obtener un agente específico
  async getAgent(id: string): Promise<Agent | null> {
    try {
      // Tu backend devuelve el agente directamente (AgentResponseDTO)
      const response = await this.client.get<Agent>(`/agents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching agent ${id}:`, error);
      return null;
    }
  }

  // Crear un nuevo agente
  async createAgent(data: CreateAgentDTO): Promise<Agent> {
    try {
      // Tu backend espera: { name: string, prompt: string }
      const response = await this.client.post<Agent>('/agents', data);
      return response.data;
    } catch (error) {
      console.error('Error creating agent:', error);
      throw error;
    }
  }

  // Actualizar un agente
  async updateAgent(id: string, data: UpdateAgentDTO): Promise<Agent> {
    try {
      const response = await this.client.put<Agent>(`/agents/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating agent ${id}:`, error);
      throw error;
    }
  }

  // Eliminar un agente
  async deleteAgent(id: string): Promise<void> {
    try {
      await this.client.delete(`/agents/${id}`);
    } catch (error) {
      console.error(`Error deleting agent ${id}:`, error);
      throw error;
    }
  }

  // ====== DOCUMENTOS ======

  // Subir un documento
  async uploadDocument(
    agentId: string, 
    file: File, 
    description?: string
  ): Promise<UploadDocumentResponse> {
    try {
      const formData = new FormData();
      formData.append('agent_id', agentId);
      formData.append('file', file);
      if (description) {
        formData.append('description', description);
      }

      const response = await this.client.post<UploadDocumentResponse>(
        '/documents/upload', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }

  // Listar documentos (con filtro opcional por agente)
  async getDocuments(agentId?: string): Promise<Document[]> {
    try {
      const params = agentId ? { agent_id: agentId } : {};
      const response = await this.client.get<Document[]>('/documents', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  }

  // Obtener información de un documento
  async getDocument(id: string): Promise<Document> {
    try {
      const response = await this.client.get<Document>(`/documents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching document ${id}:`, error);
      throw error;
    }
  }

  // Eliminar un documento
  async deleteDocument(id: string): Promise<void> {
    try {
      await this.client.delete(`/documents/${id}`);
    } catch (error) {
      console.error(`Error deleting document ${id}:`, error);
      throw error;
    }
  }

  // ====== SALUD DEL SISTEMA ======

  // Verificar estado del servidor
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await this.client.get('/health'.replace('/api/v1', ''));
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// Instancia singleton del servicio API
export const apiService = new ApiService();

// Exportar clase para testing o instancias personalizadas
export { ApiService };
