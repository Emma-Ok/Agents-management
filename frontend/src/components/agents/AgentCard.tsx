// Componente para mostrar una tarjeta de agente - Basado en diseño Figma

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Agent } from '@/types';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatRelativeTime, truncateText } from '@/lib/utils';
import { EditAgentModal } from './EditAgentModal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useUpdateAgentMutation, useDeleteAgentMutation } from '@/hooks/useAgents';

interface AgentCardProps {
  agent: Agent;
}

export function AgentCard({ agent }: AgentCardProps) {
  const router = useRouter();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  const updateAgentMutation = useUpdateAgentMutation();
  const deleteAgentMutation = useDeleteAgentMutation();

  const handleViewAgent = () => {
    router.push(`/agents/${agent.id}`);
  };

  const handleEditAgent = () => {
    setIsEditModalOpen(true);
  };

  const handleDeleteAgent = () => {
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    deleteAgentMutation.mutate(agent.id);
    setIsDeleteDialogOpen(false);
  };

  return (
    <Card className="border border-gray-200 hover:shadow-md transition-all duration-200 bg-white">
      <CardContent className="p-6">
        {/* Header con título y acciones */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {truncateText(agent.name, 30)}
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              {truncateText(agent.prompt, 120)}
            </p>
          </div>
          
          {/* Menú de acciones */}
          <div className="flex items-center gap-2 ml-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleViewAgent}
              className="text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-2"
              title="View"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEditAgent}
              className="text-gray-600 hover:text-green-600 hover:bg-green-50 px-2"
              title="Edit"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDeleteAgent}
              className="text-gray-600 hover:text-red-600 hover:bg-red-50 px-2"
              title="Delete"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </div>

        {/* Estadísticas de archivos */}
        <div className="flex items-center justify-between text-sm mb-3">
          <div className="flex items-center text-gray-600">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="font-medium">{agent.documents_count} files</span>
          </div>
          <div className="text-gray-500">
            {formatRelativeTime(agent.created_at)}
          </div>
        </div>
      </CardContent>

      {/* Edit Modal */}
      <EditAgentModal
        isOpen={isEditModalOpen}
        agent={agent}
        onClose={() => setIsEditModalOpen(false)}
        onSubmit={async (id, data) => {
          return new Promise((resolve, reject) => {
            updateAgentMutation.mutate({ id, data }, {
              onSuccess: (updatedAgent) => resolve(updatedAgent),
              onError: (error) => reject(error)
            });
          });
        }}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        title="Delete Agent"
        message={`Are you sure you want to delete "${agent.name}"? This action cannot be undone and will also delete all associated documents.`}
        confirmText="Delete Agent"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteAgentMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setIsDeleteDialogOpen(false)}
      />
    </Card>
  );
}
