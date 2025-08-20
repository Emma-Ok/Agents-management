// Hook personalizado para manejar notificaciones de operaciones CRUD lentas
'use client';

import { useCallback, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

export interface OperationConfig {
  /** ID único para la operación */
  operationId: string;
  /** Mensaje para mostrar inmediatamente */
  loadingMessage: string;
  /** Mensaje de éxito */
  successMessage: string;
  /** Mensaje de error personalizado (opcional) */
  errorMessage?: string;
  /** Tiempo en ms para mostrar notificación de operación lenta (default: 3000) */
  slowOperationThreshold?: number;
  /** Mensaje para operaciones lentas */
  slowOperationMessage?: string;
}

export interface OperationCallbacks {
  onSuccess?: (result: any) => void;
  onError?: (error: Error) => void;
  onSlowOperation?: () => void;
}

export function useOperationNotifications() {
  const slowTimers = useRef(new Map<string, NodeJS.Timeout>());

  // Limpiar timers al desmontar el componente
  useEffect(() => {
    return () => {
      slowTimers.current.forEach(timer => clearTimeout(timer));
      slowTimers.current.clear();
    };
  }, []);

  const startOperation = useCallback((config: OperationConfig, callbacks?: OperationCallbacks) => {
    const {
      operationId,
      loadingMessage,
      slowOperationThreshold = 3000,
      slowOperationMessage = "Esta operación está tardando más de lo esperado. Conectándose con AWS y MongoDB..."
    } = config;

    // Mostrar toast de loading inmediatamente
    toast.loading(loadingMessage, { id: operationId });

    // Configurar timer para operación lenta
    const slowTimer = setTimeout(() => {
      toast.loading(slowOperationMessage, { 
        id: operationId,
        duration: 10000 // Mantener visible por 10 segundos
      });
      callbacks?.onSlowOperation?.();
    }, slowOperationThreshold);

    slowTimers.current.set(operationId, slowTimer);

    return {
      complete: (result?: any, customSuccessMessage?: string) => {
        // Limpiar timer
        const timer = slowTimers.current.get(operationId);
        if (timer) {
          clearTimeout(timer);
          slowTimers.current.delete(operationId);
        }

        // Mostrar éxito
        toast.success(customSuccessMessage || config.successMessage, { 
          id: operationId,
          duration: 4000
        });

        callbacks?.onSuccess?.(result);
      },

      error: (error: Error, customErrorMessage?: string) => {
        // Limpiar timer
        const timer = slowTimers.current.get(operationId);
        if (timer) {
          clearTimeout(timer);
          slowTimers.current.delete(operationId);
        }

        // Determinar mensaje de error
        let errorMessage = customErrorMessage || config.errorMessage;
        
        if (!errorMessage) {
          // Extraer mensaje del error del backend
          errorMessage = extractErrorMessage(error);
        }

        toast.error(errorMessage, { 
          id: operationId,
          duration: 6000
        });

        callbacks?.onError?.(error);
      },

      cancel: () => {
        // Limpiar timer y toast
        const timer = slowTimers.current.get(operationId);
        if (timer) {
          clearTimeout(timer);
          slowTimers.current.delete(operationId);
        }
        toast.dismiss(operationId);
      }
    };
  }, []);

  return { startOperation };
}

/**
 * Extrae el mensaje de error más útil del error del backend
 */
function extractErrorMessage(error: Error): string {
  try {
    // Si el error tiene estructura del backend mejorado
    const errorData = (error as any)?.response?.data?.error;
    if (errorData) {
      // Usar el mensaje principal y agregar acción si está disponible
      let message = errorData.message || 'Error desconocido';
      if (errorData.details?.action) {
        message += ` - ${errorData.details.action}`;
      }
      return message;
    }

    // Fallback a mensaje del error
    return error.message || 'Ha ocurrido un error inesperado';
  } catch {
    return 'Ha ocurrido un error inesperado';
  }
}

/**
 * Hook específico para operaciones de agentes
 */
export function useAgentOperationNotifications() {
  const { startOperation } = useOperationNotifications();

  return {
    createAgent: (agentName: string, callbacks?: OperationCallbacks) => 
      startOperation({
        operationId: 'create-agent',
        loadingMessage: `Creando agente "${agentName}"...`,
        successMessage: `Agente "${agentName}" creado exitosamente`,
        errorMessage: 'Error al crear el agente',
        slowOperationMessage: 'Creando agente y configurando carpeta en AWS S3. Esto puede tardar un momento...'
      }, callbacks),

    updateAgent: (agentName: string, callbacks?: OperationCallbacks) => 
      startOperation({
        operationId: 'update-agent',
        loadingMessage: `Actualizando agente "${agentName}"...`,
        successMessage: `Agente "${agentName}" actualizado exitosamente`,
        errorMessage: 'Error al actualizar el agente',
        slowOperationThreshold: 2000
      }, callbacks),

    deleteAgent: (agentName: string, callbacks?: OperationCallbacks) => 
      startOperation({
        operationId: 'delete-agent',
        loadingMessage: `Eliminando agente "${agentName}"...`,
        successMessage: `Agente "${agentName}" eliminado exitosamente`,
        errorMessage: 'Error al eliminar el agente',
        slowOperationMessage: 'Eliminando agente y todos sus documentos de AWS S3 y MongoDB...'
      }, callbacks)
  };
}

/**
 * Hook específico para operaciones de documentos
 */
export function useDocumentOperationNotifications() {
  const { startOperation } = useOperationNotifications();

  return {
    uploadDocument: (fileName: string, callbacks?: OperationCallbacks) => 
      startOperation({
        operationId: `upload-${fileName}`,
        loadingMessage: `Subiendo "${fileName}"...`,
        successMessage: `Documento "${fileName}" subido exitosamente`,
        errorMessage: 'Error al subir el documento',
        slowOperationMessage: 'Subiendo documento a AWS S3 y registrando en MongoDB. Archivos grandes pueden tardar más...'
      }, callbacks),

    deleteDocument: (fileName: string, callbacks?: OperationCallbacks) => 
      startOperation({
        operationId: `delete-${fileName}`,
        loadingMessage: `Eliminando "${fileName}"...`,
        successMessage: `Documento "${fileName}" eliminado exitosamente`,
        errorMessage: 'Error al eliminar el documento',
        slowOperationThreshold: 2000
      }, callbacks)
  };
}
