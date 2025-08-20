// Componente de upload de documentos con drag & drop
'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useDocumentUpload } from '@/hooks/useDocuments';
import { useDocumentOperationNotifications } from '@/hooks/useOperationNotifications';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { formatFileSize } from '@/lib/utils';
import { validateFile } from '@/lib/validations';
import toast from 'react-hot-toast';

interface DocumentUploadProps {
  agentId: string;
  onUploadComplete?: () => void;
  onClose?: () => void;
}

export function DocumentUpload({ agentId, onUploadComplete, onClose }: DocumentUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [currentlyUploading, setCurrentlyUploading] = useState<string | null>(null);
  const { uploadDocument, isUploading } = useDocumentUpload();
  const { uploadDocument: notifyUpload } = useDocumentOperationNotifications();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Validar archivos usando las validaciones sincronizadas
    const validFiles = acceptedFiles.filter(file => {
      const validation = validateFile(file, selectedFiles.length);
      
      if (!validation.isValid) {
        toast.error(`${file.name}: ${validation.error}`);
        return false;
      }
      
      // Informar sobre caracteres especiales (solo informativo)
      const hasSpecialChars = /[^\x00-\x7F]/.test(file.name);
      if (hasSpecialChars) {
        console.log(`📝 Archivo con caracteres especiales: "${file.name}" - será sanitizado automáticamente`);
      }
      
      return true;
    });

    if (validFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...validFiles]);
      if (validFiles.length < acceptedFiles.length) {
        toast.error(`${acceptedFiles.length - validFiles.length} archivo(s) rechazado(s)`);
      }
    }
  }, [selectedFiles.length]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    multiple: true,
    disabled: isUploading
  });

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    // Mostrar notificación general para múltiples archivos
    toast.loading(`Subiendo ${selectedFiles.length} archivo(s)...`, { id: 'upload-batch' });

    try {
      let successCount = 0;
      let errorCount = 0;

      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const fileId = `${file.name}-${Date.now()}`;
        
        // Establecer archivo actual
        setCurrentlyUploading(file.name);
        
        // Inicializar progreso
        setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));
        
        // Progreso simulado más realista
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => ({
            ...prev,
            [fileId]: Math.min(prev[fileId] + Math.random() * 15 + 5, 85)
          }));
        }, 300);

        // Crear operación de notificación para este archivo
        const operation = notifyUpload(file.name, {
          onSuccess: () => {
            successCount++;
            // Remover archivo de la lista después de subirlo
            setTimeout(() => {
              setSelectedFiles(prev => prev.filter(f => f !== file));
              setUploadProgress(prev => {
                const newProgress = { ...prev };
                delete newProgress[fileId];
                return newProgress;
              });
            }, 1500);
          },
          onError: () => {
            errorCount++;
          }
        });

        try {
          const result = await uploadDocument({ agentId, file });
          
          clearInterval(progressInterval);
          setUploadProgress(prev => ({ ...prev, [fileId]: 100 }));
          
          operation.complete(result);
          
        } catch (fileError) {
          clearInterval(progressInterval);
          setUploadProgress(prev => {
            const newProgress = { ...prev };
            delete newProgress[fileId];
            return newProgress;
          });
          
          operation.error(fileError as Error);
        }
      }

      // Limpiar estado
      setCurrentlyUploading(null);
      
      // Mostrar resumen final
      if (errorCount === 0) {
        toast.success(`${successCount} archivo(s) subido(s) exitosamente`, { id: 'upload-batch' });
      } else if (successCount > 0) {
        toast.success(`${successCount} archivo(s) subido(s), ${errorCount} falló(s)`, { id: 'upload-batch' });
      } else {
        toast.error(`Error subiendo todos los archivos`, { id: 'upload-batch' });
      }
      
      // Notificar completado si hay éxitos
      if (successCount > 0) {
        onUploadComplete?.();
      }
      
    } catch (error) {
      console.error('Error uploading files:', error);
      setCurrentlyUploading(null);
      toast.error('Error en la subida de archivos', { id: 'upload-batch' });
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return '📄';
      case 'docx': return '📝';
      case 'xlsx': return '📊';
      case 'pptx': return '📋';
      case 'txt': return '📄';
      case 'csv': return '📈';
      default: return '📎';
    }
  };

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        {/* Upload Status */}
        {isUploading && currentlyUploading && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900">
                  Subiendo archivo...
                </p>
                <p className="text-xs text-blue-600 truncate">
                  {currentlyUploading}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Drop Zone */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-black bg-gray-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
            ${isUploading ? 'cursor-not-allowed opacity-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </div>
            
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Drop files here...' : 'Upload Documents'}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Drag and drop files here, or click to browse
              </p>
            </div>
            
            <div className="text-xs text-gray-500">
              <p>Supported formats: PDF, DOCX, XLSX, PPTX, TXT, CSV</p>
              <p>Maximum file size: 20MB • Maximum 50 files per agent</p>
            </div>
          </div>
        </div>

        {/* File List */}
        {selectedFiles.length > 0 && (
          <div className="mt-6 space-y-3">
            <h4 className="font-medium text-gray-900">Selected Files ({selectedFiles.length})</h4>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {selectedFiles.map((file, index) => {
                const fileId = `${file.name}-${Date.now()}`;
                const progress = uploadProgress[fileId] || 0;
                
                const isCurrentFile = currentlyUploading === file.name;
                const isCompleted = progress >= 100;
                
                return (
                  <div 
                    key={index} 
                    className={`flex items-center justify-between p-3 rounded-lg transition-all duration-200 ${
                      isCurrentFile ? 'bg-blue-50 border border-blue-200' : 
                      isCompleted ? 'bg-green-50 border border-green-200' : 
                      'bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <div className="relative">
                        <span className="text-2xl">{getFileIcon(file.name)}</span>
                        {isCurrentFile && (
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full animate-pulse"></div>
                        )}
                        {isCompleted && (
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-600 rounded-full flex items-center justify-center">
                            <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`font-medium text-sm truncate ${
                          isCurrentFile ? 'text-blue-900' : 
                          isCompleted ? 'text-green-900' : 
                          'text-gray-900'
                        }`}>
                          {file.name}
                        </p>
                        <p className={`text-xs ${
                          isCurrentFile ? 'text-blue-600' : 
                          isCompleted ? 'text-green-600' : 
                          'text-gray-500'
                        }`}>
                          {formatFileSize(file.size)}
                          {isCurrentFile && ' • Subiendo...'}
                          {isCompleted && ' • Completado'}
                        </p>
                        
                        {/* Progress Bar */}
                        {progress > 0 && progress < 100 && (
                          <div className="mt-2">
                            <div className="bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-blue-600 mt-1">{Math.round(progress)}%</p>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {!isUploading && !isCompleted && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-gray-400 hover:text-red-600 ml-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 mt-6">
          {onClose && (
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isUploading}
            >
              Cancel
            </Button>
          )}
          <Button
            onClick={uploadFiles}
            disabled={selectedFiles.length === 0 || isUploading}
            isLoading={isUploading}
            className="bg-black hover:bg-gray-800 text-white"
          >
            {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} file${selectedFiles.length !== 1 ? 's' : ''}`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
