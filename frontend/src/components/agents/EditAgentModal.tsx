// Modal para editar un agente existente
'use client';

import React, { useState, useEffect } from 'react';
import { Agent, UpdateAgentDTO } from '@/types';
import { Button } from '@/components/ui/Button';
import { validateAgentNameLegacy, validateAgentPromptLegacy } from '@/lib/validations';
import { useAgentOperationNotifications } from '@/hooks/useOperationNotifications';

interface EditAgentModalProps {
  isOpen: boolean;
  agent: Agent | null;
  onClose: () => void;
  onSubmit: (id: string, data: UpdateAgentDTO) => Promise<Agent>;
}

export function EditAgentModal({ isOpen, agent, onClose, onSubmit }: EditAgentModalProps) {
  const [formData, setFormData] = useState<UpdateAgentDTO>({
    name: '',
    prompt: '',
  });
  const [errors, setErrors] = useState<{ name?: string; prompt?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { updateAgent } = useAgentOperationNotifications();

  // Cargar datos del agente cuando se abre el modal
  useEffect(() => {
    if (agent && isOpen) {
      setFormData({
        name: agent.name,
        prompt: agent.prompt,
      });
      setErrors({});
    }
  }, [agent, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!agent) return;

    // Validar formulario
    const nameError = validateAgentNameLegacy(formData.name || '');
    const promptError = validateAgentPromptLegacy(formData.prompt || '');
    
    if (nameError || promptError) {
      setErrors({ name: nameError || undefined, prompt: promptError || undefined });
      return;
    }

    setIsSubmitting(true);
    setErrors({});
    
    // Usar el sistema de notificaciones mejorado
    const operation = updateAgent(agent.name, {
      onSuccess: () => {
        onClose();
        setIsSubmitting(false);
      },
      onError: (error) => {
        const errorMessage = (error as any)?.details?.action 
          ? `${error.message}` 
          : error.message;
        
        setErrors({ 
          name: errorMessage
        });
        setIsSubmitting(false);
      }
    });

    try {
      const result = await onSubmit(agent.id, formData);
      operation.complete(result);
    } catch (error) {
      operation.error(error as Error);
    }
  };

  const handleClose = () => {
    setErrors({});
    onClose();
  };

  if (!isOpen || !agent) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Edit Agent
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Subtítulo */}
        <div className="px-6 pt-4">
          <p className="text-sm text-gray-600">
            Update the configuration for this AI agent
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 pt-4">
          <div className="space-y-5">
            {/* Nombre del Agente */}
            <div>
              <label htmlFor="edit-name" className="block text-sm font-medium text-gray-900 mb-2">
                Name *
              </label>
              <input
                type="text"
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={`w-full px-3 py-2.5 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black transition-colors ${
                  errors.name ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                }`}
                placeholder="Enter agent name"
                disabled={isSubmitting}
              />
              {errors.name && (
                <p className="mt-1.5 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            {/* System Prompt */}
            <div>
              <label htmlFor="edit-prompt" className="block text-sm font-medium text-gray-900 mb-2">
                System Prompt *
              </label>
              <textarea
                id="edit-prompt"
                rows={5}
                value={formData.prompt}
                onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                className={`w-full px-3 py-2.5 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black transition-colors resize-none ${
                  errors.prompt ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                }`}
                placeholder="Enter the system prompt for this agent"
                disabled={isSubmitting}
              />
              {errors.prompt && (
                <p className="mt-1.5 text-sm text-red-600">{errors.prompt}</p>
              )}
              <p className="mt-1.5 text-xs text-gray-500">
                This prompt will define how the agent behaves and responds to user queries.
              </p>
            </div>
          </div>

          {/* Acciones */}
          <div className="flex justify-end gap-3 mt-8">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-6"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              className="px-6 bg-black hover:bg-gray-800 text-white"
            >
              {isSubmitting ? 'Updating...' : 'Update Agent'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
