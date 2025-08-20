// Tipos base para la aplicación de gestión de agentes IA - ADAPTADOS AL BACKEND EXISTENTE

export interface UploadDocumentDTO {
  agent_id: string;
  file: File;
  description?: string;
  metadata?: Record<string, unknown>;
}

// Tipo para el elemento de lista (lo que devuelve tu backend en listAgents)
export interface AgentListItem {
  id: string;
  documents_count: number;
  created_at: string;
}

// Tipo completo del agente (para detalles individuales)
export interface Agent {
  id: string;
  name: string;
  prompt: string;
  documents_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentDTO {
  name: string;
  prompt: string;
}

export interface UpdateAgentDTO {
  name?: string;
  prompt?: string;
}

export interface Document {
  id: string;
  agent_id: string;
  filename: string;
  document_type: 'pdf' | 'docx' | 'xlsx' | 'pptx' | 'txt' | 'csv';
  file_url: string;
  file_size: number;
  file_size_mb: number;
  created_at: string;
}

export interface UploadDocumentResponse {
  success: boolean;
  message: string;
  data: {
    document: Document;
    file_info: {
      name: string;
      size: number;
      size_mb: number;
      type: string;
    };
    upload_status: string;
  };
}

// Respuesta de tu backend para listAgents (formato exacto)
export interface AgentsListResponse {
  items: AgentListItem[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
  next_skip: number | null;
}

// Respuesta genérica para endpoints individuales
export interface ApiResponse<T> {
  success?: boolean;
  message?: string;
  timestamp?: string;
  data?: T;
}

export interface ApiError {
  detail?: string;
  message?: string;
  error?: string;
}

// Estados de la UI
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface UploadState {
  isUploading: boolean;
  progress: number;
  error?: string | null;
  success?: boolean;
}
