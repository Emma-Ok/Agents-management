// Modal para crear un nuevo agente

import React, { useState } from 'react';
import { CreateAgentDTO, Agent } from '@/types';
import { Button } from '@/components/ui/Button';
import { validateAgentName, validateAgentPrompt } from '@/lib/utils';

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateAgentDTO) => Promise<Agent>;
}

export function CreateAgentModal({ isOpen, onClose, onSubmit }: CreateAgentModalProps) {
  const [formData, setFormData] = useState<CreateAgentDTO>({
    name: '',
    prompt: '',
  });
  const [errors, setErrors] = useState<{ name?: string; prompt?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar formulario
    const nameError = validateAgentName(formData.name);
    const promptError = validateAgentPrompt(formData.prompt);
    
    if (nameError || promptError) {
      setErrors({ name: nameError || undefined, prompt: promptError || undefined });
      return;
    }

    try {
      setIsSubmitting(true);
      setErrors({});
      await onSubmit(formData);
      
      // Limpiar formulario y cerrar modal
      setFormData({ name: '', prompt: '' });
      onClose();
    } catch (error) {
      setErrors({ 
        name: error instanceof Error ? error.message : 'Error al crear agente' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setFormData({ name: '', prompt: '' });
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Crear Nuevo Agente
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            {/* Nombre del Agente */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Nombre del Agente *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: Asistente de Documentos"
                disabled={isSubmitting}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            {/* Prompt del Agente */}
            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
                Prompt del Agente *
              </label>
              <textarea
                id="prompt"
                rows={4}
                value={formData.prompt}
                onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.prompt ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Describe las instrucciones y comportamiento que quieres que tenga tu agente..."
                disabled={isSubmitting}
              />
              {errors.prompt && (
                <p className="mt-1 text-sm text-red-600">{errors.prompt}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                Caracteres: {formData.prompt.length}/5000
              </p>
            </div>
          </div>

          {/* Acciones */}
          <div className="flex gap-3 mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              className="flex-1"
            >
              {isSubmitting ? 'Creando...' : 'Crear Agente'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
