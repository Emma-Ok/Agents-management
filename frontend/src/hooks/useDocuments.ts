// Hook personalizado para manejar operaciones con documentos - USANDO AXIOS

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiAxios';
import { Document, UploadState } from '@/types';

export function useDocumentUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
  });

  const uploadDocument = useCallback(async (
    agentId: string,
    file: File,
    description?: string
  ): Promise<Document> => {
    try {
      setUploadState({
        isUploading: true,
        progress: 0,
        error: null,
        success: false,
      });

      // Simular progreso (en una implementación real, podrías usar XMLHttpRequest para tracking real)
      const progressInterval = setInterval(() => {
        setUploadState(prev => ({
          ...prev,
          progress: Math.min(prev.progress + 10, 90),
        }));
      }, 100);

      const response = await apiService.uploadDocument(agentId, file, description);
      
      clearInterval(progressInterval);
      
      setUploadState({
        isUploading: false,
        progress: 100,
        success: true,
      });

      return response.data.document;
    } catch (error) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: error instanceof Error ? error.message : 'Error al subir documento',
        success: false,
      });
      throw error;
    }
  }, []);

  const resetUploadState = useCallback(() => {
    setUploadState({
      isUploading: false,
      progress: 0,
    });
  }, []);

  return {
    uploadState,
    uploadDocument,
    resetUploadState,
  };
}

export function useDocuments(agentId?: string) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getDocuments(agentId);
      setDocuments(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar documentos');
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  const deleteDocument = useCallback(async (documentId: string): Promise<void> => {
    try {
      await apiService.deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (error) {
      throw error instanceof Error ? error : new Error('Error al eliminar documento');
    }
  }, []);

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    deleteDocument,
  };
}
