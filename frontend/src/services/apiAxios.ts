// Servicio de API con Axios - ADAPTADO AL BACKEND EXISTENTE

import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  Agent, 
  AgentsListResponse,
  CreateAgentDTO, 
  UpdateAgentDTO, 
  Document, 
  UploadDocumentResponse
} from '@/types';

// Tipos para respuestas de error del backend
interface BackendErrorResponse {
  success: boolean;
  error: {
    type: string;
    message: string;
    timestamp: string;
    status_code: number;
    details?: {
      action?: string;
      [key: string]: unknown;
    };
  };
}

// Tipo para datos de error legacy
interface LegacyErrorData {
  detail?: string;
  message?: string;
  error?: string;
  [key: string]: unknown;
}

// Configuración base de la API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2 minutos para uploads grandes
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Interceptor para logging
          this.client.interceptors.request.use(
        (config) => {
          console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            params: config.params,
            headers: config.headers
          });
          return config;
        },
        (error) => {
          console.error('❌ Request Error:', error);
          return Promise.reject(error);
        }
      );

    // Interceptor para respuestas - simplificado
    this.client.interceptors.response.use(
      (response) => {
        if (process.env.NODE_ENV === 'development') {
          console.log(`✅ API Response: ${response.status}`, response.data);
        }
        return response;
      },
      (error: AxiosError | Error) => {
        const handledError = this.handleError(error);
        return Promise.reject(handledError);
      }
    );
  }

  private handleError(error: AxiosError | Error): Error {
    // Log de debugging para desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.error('🔍 API Error Details:', {
        type: error.constructor.name,
        message: error.message,
        status: 'response' in error ? error.response?.status : undefined,
        data: 'response' in error ? error.response?.data : undefined,
        code: 'code' in error ? error.code : undefined
      });
    }

    // Validar que el error sea un objeto válido
    if (!error || typeof error !== 'object') {
      return new Error('Error desconocido en la comunicación con el servidor');
    }

    // Manejar errores de conexión/red
    const errorCode = 'code' in error ? error.code : undefined;
    if (errorCode === 'ECONNREFUSED' || errorCode === 'ERR_NETWORK') {
      return new Error('No se puede conectar al servidor. Verifica que el backend esté ejecutándose.');
    }
    
    if (errorCode === 'ECONNABORTED' || errorCode === 'ETIMEDOUT' || error.message?.includes('timeout')) {
      return new Error('La operación tardó demasiado tiempo. Las operaciones con AWS pueden ser lentas, inténtalo de nuevo.');
    }
    
    // Manejar errores HTTP con respuesta del servidor
    if ('response' in error && error.response) {
      const errorData = error.response.data as BackendErrorResponse | LegacyErrorData;
      
      // Manejar formato mejorado del backend: {success: false, error: {...}}
      if ('error' in errorData && errorData.error && typeof errorData.error === 'object') {
        const backendErrorResponse = errorData as BackendErrorResponse;
        const backendError = backendErrorResponse.error;
        let message = backendError.message || 'Error del servidor';
        
        // Agregar información adicional si está disponible
        if (backendError.details?.action) {
          message += ` | ${backendError.details.action}`;
        }
        
        // Crear error extendido con información adicional
        const enhancedError = new Error(message) as Error & {
          type?: string;
          status?: number;
          details?: BackendErrorResponse['error']['details'];
        };
        enhancedError.type = backendError.type;
        enhancedError.status = error.response.status;
        enhancedError.details = backendError.details;
        
        return enhancedError;
      }
      
      // Manejar formato legacy
      const legacyData = errorData as LegacyErrorData;
      const message = legacyData.detail || 
                     legacyData.message || 
                     legacyData.error ||
                     `Error ${error.response.status}: ${error.response.statusText}`;
      
      const enhancedError = new Error(message) as Error & { status?: number };
      enhancedError.status = error.response.status;
      return enhancedError;
    }
    
    // Error sin respuesta (problemas de red)
    return new Error(`Error de conexión: ${error.message || 'No se pudo comunicar con el servidor'}`);
  }

  // ====== AGENTES ======

  // Listar todos los agentes (adaptado al formato real del backend)
  async getAgents(skip: number = 0, limit: number = 20): Promise<{ agents: Agent[]; total: number }> {
    try {
      // El backend devuelve: { items: AgentListItemDTO[], total: number, ... }
      const response = await this.client.get<AgentsListResponse>('/agents', {
        params: { skip, limit }
      });

      console.log('🔍 Respuesta del backend (agents list):', response.data);

      // Optimización: Usar Promise.all para cargar detalles en paralelo
      const agentPromises = response.data.items.map(async (item) => {
        try {
          const agentDetail = await this.getAgent(item.id);
          return agentDetail || {
            id: item.id,
            name: `Agente ${item.id.substring(0, 8)}`,
            prompt: 'No disponible',
            documents_count: item.documents_count,
            created_at: item.created_at,
            updated_at: item.created_at
          };
        } catch (error) {
          console.warn(`No se pudo cargar detalle del agente ${item.id}:`, error);
          return {
            id: item.id,
            name: `Agente ${item.id.substring(0, 8)}`,
            prompt: 'No disponible',
            documents_count: item.documents_count,
            created_at: item.created_at,
            updated_at: item.created_at
          };
        }
      });

      const agentDetails = await Promise.all(agentPromises);

      console.log('✅ Agentes con detalles cargados:', agentDetails.length);

      return {
        agents: agentDetails,
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
      // El backend devuelve un dict con 'agent' y 'documents' para GetAgentDetail
      const response = await this.client.get(`/agents/${id}`);
      
      console.log(`🔍 Respuesta del backend (agent detail ${id}):`, response.data);
      
      // Si la respuesta tiene estructura { agent: AgentResponseDTO, documents: [] }
      if (response.data.agent) {
        const agentData = response.data.agent;
        return {
          id: agentData.id,
          name: agentData.name,
          prompt: agentData.prompt,
          documents_count: agentData.documents_count,
          created_at: agentData.created_at,
          updated_at: agentData.updated_at
        };
      }
      
      // Si la respuesta es directamente AgentResponseDTO (fallback)
      if (response.data.id) {
        return {
          id: response.data.id,
          name: response.data.name,
          prompt: response.data.prompt,
          documents_count: response.data.documents_count,
          created_at: response.data.created_at,
          updated_at: response.data.updated_at
        };
      }
      
      console.warn(`Estructura de respuesta inesperada para agente ${id}:`, response.data);
      return null;
    } catch (error) {
      console.error(`Error fetching agent ${id}:`, error);
      return null;
    }
  }

  // Crear un nuevo agente
  async createAgent(data: CreateAgentDTO): Promise<Agent> {
    console.log('🚀 Creating agent with data:', data);
    
    // El backend espera: { name: string, prompt: string }
    // Y devuelve directamente AgentResponseDTO
    // Usar timeout extendido para creación de agentes (incluye creación de S3 folder)
    const response = await this.client.post('/agents', data, {
      timeout: 60000 // 1 minuto para creación de agentes
    });
    
    console.log('✅ Agent creation response:', response.data);
    
    // El backend devuelve directamente AgentResponseDTO
    if (response.data.id) {
      const agentData = response.data;
      return {
        id: agentData.id,
        name: agentData.name,
        prompt: agentData.prompt,
        documents_count: agentData.documents_count,
        created_at: agentData.created_at,
        updated_at: agentData.updated_at
      };
    }
    
    throw new Error('Respuesta del backend inválida al crear agente');
  }

  // Actualizar un agente
  async updateAgent(id: string, data: UpdateAgentDTO): Promise<Agent> {
    try {
      // El backend devuelve directamente AgentResponseDTO
      const response = await this.client.put(`/agents/${id}`, data);
      
      console.log('✅ Agent update response:', response.data);
      
      if (response.data.id) {
        const agentData = response.data;
        return {
          id: agentData.id,
          name: agentData.name,
          prompt: agentData.prompt,
          documents_count: agentData.documents_count,
          created_at: agentData.created_at,
          updated_at: agentData.updated_at
        };
      }
      
      throw new Error('Respuesta del backend inválida al actualizar agente');
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

      const response = await this.client.post(
        '/documents/upload', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      console.log('✅ Document upload response:', response.data);
      console.log('✅ Response status:', response.status);
      console.log('✅ Response headers:', response.headers);
      
      // El backend devuelve estructura con ResponseFormatter
      if (response.data.success && response.data.data) {
        return {
          success: true,
          message: response.data.message,
          data: response.data.data
        };
      }
      
      throw new Error('Formato de respuesta inesperado para upload de documento');
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }

  // Listar documentos (con filtro opcional por agente)
  async getDocuments(agentId?: string): Promise<Document[]> {
    try {
      const params = agentId ? { agent_id: agentId } : {};
      const response = await this.client.get('/documents/', { params });
      
      console.log('🔍 Respuesta del backend (documents):', response.data);
      
      // El backend devuelve estructura con ResponseFormatter
      if (response.data.success && response.data.data) {
        const documentsData = response.data.data.documents || response.data.data;
        
        if (Array.isArray(documentsData)) {
          return documentsData.map((doc: Record<string, unknown>) => ({
            id: doc.id as string,
            agent_id: doc.agent_id as string,
            filename: doc.filename as string,
            document_type: doc.document_type as 'pdf' | 'docx' | 'xlsx' | 'pptx' | 'txt' | 'csv',
            file_url: doc.file_url as string,
            file_size: doc.file_size as number,
            file_size_mb: doc.file_size_mb as number,
            created_at: doc.created_at as string
          }));
        }
      }
      
      // Fallback: si es array directo
      if (Array.isArray(response.data)) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  }

  // Obtener información de un documento
  async getDocument(id: string): Promise<Document> {
    try {
      const response = await this.client.get(`/documents/${id}`);
      
      console.log(`🔍 Respuesta del backend (document ${id}):`, response.data);
      
      // El backend devuelve estructura con ResponseFormatter
      if (response.data.success && response.data.data && response.data.data.document) {
        const doc = response.data.data.document;
        return {
          id: doc.id,
          agent_id: doc.agent_id,
          filename: doc.filename,
          document_type: doc.document_type,
          file_url: doc.file_url,
          file_size: doc.file_size,
          file_size_mb: doc.file_size_mb,
          created_at: doc.created_at
        };
      }
      
      // Fallback: si es objeto directo
      if (response.data.id) {
        return response.data;
      }
      
      throw new Error('Formato de respuesta inesperado para documento');
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
