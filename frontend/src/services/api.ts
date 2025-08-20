// Servicio de API para conectar con el backend FastAPI

import { 
  Agent, 
  CreateAgentDTO, 
  UpdateAgentDTO, 
  Document, 
  ApiResponse, 
  PaginatedResponse, 
  UploadDocumentResponse 
} from '@/types';

// Configuración base de la API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Método helper para hacer requests
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Método helper para uploads con FormData
  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Upload Error (${endpoint}):`, error);
      throw error;
    }
  }

  // ====== AGENTES ======

  // Listar todos los agentes
  async getAgents(): Promise<ApiResponse<Agent[]>> {
    return this.request<ApiResponse<Agent[]>>('/agents');
  }

  // Obtener un agente específico
  async getAgent(id: string): Promise<ApiResponse<Agent>> {
    return this.request<ApiResponse<Agent>>(`/agents/${id}`);
  }

  // Crear un nuevo agente
  async createAgent(data: CreateAgentDTO): Promise<ApiResponse<Agent>> {
    return this.request<ApiResponse<Agent>>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Actualizar un agente
  async updateAgent(id: string, data: UpdateAgentDTO): Promise<ApiResponse<Agent>> {
    return this.request<ApiResponse<Agent>>(`/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Eliminar un agente
  async deleteAgent(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<ApiResponse<{ deleted: boolean }>>(`/agents/${id}`, {
      method: 'DELETE',
    });
  }

  // ====== DOCUMENTOS ======

  // Subir un documento
  async uploadDocument(
    agentId: string, 
    file: File, 
    description?: string
  ): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('agent_id', agentId);
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    return this.uploadRequest<UploadDocumentResponse>('/documents/upload', formData);
  }

  // Listar documentos (con filtro opcional por agente)
  async getDocuments(agentId?: string): Promise<PaginatedResponse<Document>> {
    const params = agentId ? `?agent_id=${agentId}` : '';
    return this.request<PaginatedResponse<Document>>(`/documents${params}`);
  }

  // Obtener información de un documento
  async getDocument(id: string): Promise<ApiResponse<Document>> {
    return this.request<ApiResponse<Document>>(`/documents/${id}`);
  }

  // Eliminar un documento
  async deleteDocument(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<ApiResponse<{ deleted: boolean }>>(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // ====== SALUD DEL SISTEMA ======

  // Verificar estado del servidor
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${this.baseURL.replace('/api/v1', '')}/health`);
    return response.json();
  }
}

// Instancia singleton del servicio API
export const apiService = new ApiService();

// Exportar clase para testing o instancias personalizadas
export { ApiService };
