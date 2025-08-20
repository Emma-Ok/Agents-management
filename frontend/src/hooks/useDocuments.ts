// Hook personalizado para manejar operaciones con documentos - USANDO REACT QUERY + AXIOS

import { 
  useDocuments, 
  useDocumentsQuery, 
  useDocumentQuery,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useDocumentUpload,
  DOCUMENT_QUERY_KEYS 
} from './useDocumentsQuery';

// Re-exportar hooks de React Query para compatibilidad
export { 
  useDocuments, 
  useDocumentsQuery, 
  useDocumentQuery,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useDocumentUpload,
  DOCUMENT_QUERY_KEYS 
};

// Hook legado para compatibilidad (deprecated)
export function useDocumentsLegacy(agentId?: string) {
  console.warn('useDocumentsLegacy is deprecated. Use useDocuments from useDocumentsQuery instead.');
  return useDocuments(agentId);
}
