// Hook personalizado usando React Query para manejar documentos
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/apiAxios';
import { Document, UploadDocumentResponse } from '@/types';
import toast from 'react-hot-toast';
import { QUERY_KEYS } from './useAgentsQuery';

// Query Keys específicos para documentos
export const DOCUMENT_QUERY_KEYS = {
  documents: ['documents'] as const,
  document: (id: string) => ['documents', id] as const,
  documentsByAgent: (agentId: string) => ['documents', 'agent', agentId] as const,
};

// Hook para listar documentos (con filtro opcional por agente)
export function useDocumentsQuery(agentId?: string) {
  return useQuery({
    queryKey: agentId 
      ? DOCUMENT_QUERY_KEYS.documentsByAgent(agentId)
      : DOCUMENT_QUERY_KEYS.documents,
    queryFn: () => apiService.getDocuments(agentId),
    staleTime: 2 * 60 * 1000, // 2 minutos (menos cache para documentos)
    retry: 3,
    meta: {
      errorMessage: agentId 
        ? `Error al cargar documentos del agente ${agentId}`
        : 'Error al cargar documentos',
    },
  });
}

// Hook para obtener un documento específico
export function useDocumentQuery(id: string) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.document(id),
    queryFn: () => apiService.getDocument(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    retry: 3,
    meta: {
      errorMessage: `Error al cargar el documento ${id}`,
    },
  });
}

// Hook para subir documentos
export function useUploadDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ 
      agentId, 
      file, 
      description 
    }: { 
      agentId: string; 
      file: File; 
      description?: string; 
    }) => apiService.uploadDocument(agentId, file, description),
    
    onSuccess: (response, { agentId }) => {
      console.log('✅ Document upload response:', response);
      
      let documentData;
      
      // Manejar diferentes formatos de respuesta del backend
      if (response.data?.document) {
        documentData = response.data.document;
      } else if (response.success && response.data?.document) {
        documentData = response.data.document;
      } else if ('filename' in response && response.filename) {
        documentData = response; // La respuesta es directamente el documento
      } else {
        console.warn('⚠️ Formato de respuesta inesperado:', response);
        documentData = { filename: 'Documento subido' };
      }
      
      // Invalidar cache de documentos
      queryClient.invalidateQueries({ 
        queryKey: DOCUMENT_QUERY_KEYS.documentsByAgent(agentId) 
      });
      queryClient.invalidateQueries({ 
        queryKey: DOCUMENT_QUERY_KEYS.documents 
      });
      
      // Invalidar cache del agente para actualizar document_count
      queryClient.invalidateQueries({ 
        queryKey: QUERY_KEYS.agent(agentId) 
      });
      queryClient.invalidateQueries({ 
        queryKey: QUERY_KEYS.agents 
      });

      // No enviamos toast aquí - se maneja en useDocumentOperationNotifications
    },
    
    onError: (error: Error) => {
      // No enviamos toast aquí - se maneja en useDocumentOperationNotifications
    },
  });
}

// Hook para eliminar documentos
export function useDeleteDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiService.deleteDocument(id),
    
    onSuccess: (_, documentId) => {
      // Remover del cache específico
      queryClient.removeQueries({ 
        queryKey: DOCUMENT_QUERY_KEYS.document(documentId) 
      });
      
      // Invalidar listas de documentos
      queryClient.invalidateQueries({ 
        queryKey: DOCUMENT_QUERY_KEYS.documents 
      });
      queryClient.invalidateQueries({ 
        predicate: (query) => {
          const queryKey = query.queryKey;
          return queryKey[0] === 'documents' && queryKey[1] === 'agent';
        }
      });
      
      // Invalidar cache de agentes para actualizar document_count
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.agents });

      toast.success('Documento eliminado exitosamente');
    },
    
    onError: (error: Error) => {
      toast.error(`Error al eliminar documento: ${error.message}`);
    },
  });
}

// Hook combinado para facilitar el uso
export function useDocuments(agentId?: string) {
  const documentsQuery = useDocumentsQuery(agentId);
  const uploadMutation = useUploadDocumentMutation();
  const deleteMutation = useDeleteDocumentMutation();

  return {
    // Data
    documents: documentsQuery.data || [],
    
    // Loading states
    isLoading: documentsQuery.isLoading,
    isError: documentsQuery.isError,
    error: documentsQuery.error,
    
    // Actions
    uploadDocument: (file: File, description?: string) => {
      if (!agentId) {
        throw new Error('Agent ID is required for document upload');
      }
      return uploadMutation.mutate({ agentId, file, description });
    },
    deleteDocument: deleteMutation.mutate,
    
    // Mutation states
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
    uploadProgress: uploadMutation.isPending ? 50 : 0, // Mock progress
    
    // Utilities
    refetch: documentsQuery.refetch,
  };
}

// Hook específico para subida con estado detallado
export function useDocumentUpload() {
  const uploadMutation = useUploadDocumentMutation();

  return {
    uploadDocument: uploadMutation.mutateAsync, // Usar mutateAsync para promesas
    isUploading: uploadMutation.isPending,
    isSuccess: uploadMutation.isSuccess,
    isError: uploadMutation.isError,
    error: uploadMutation.error,
    reset: uploadMutation.reset,
    data: uploadMutation.data,
  };
}
