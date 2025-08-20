// Componente para mostrar una tarjeta de agente

import React from 'react';
import { useRouter } from 'next/navigation';
import { Agent } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatRelativeTime, truncateText } from '@/lib/utils';

interface AgentCardProps {
  agent: Agent;
}

export function AgentCard({ agent }: AgentCardProps) {
  const router = useRouter();

  const handleViewDetails = () => {
    router.push(`/agents/${agent.id}`);
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 mb-2">
              {truncateText(agent.name, 25)}
            </CardTitle>
            <p className="text-sm text-gray-600">
              {truncateText(agent.prompt, 100)}
            </p>
          </div>
          <div className="ml-4 flex-shrink-0">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg 
                className="w-6 h-6 text-blue-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" 
                />
              </svg>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Estadísticas */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <svg 
                className="w-4 h-4 mr-1" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                />
              </svg>
              <span>{agent.documents_count} documentos</span>
            </div>
            <div className="text-gray-500">
              {formatRelativeTime(agent.created_at)}
            </div>
          </div>

          {/* Estado del agente */}
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Activo</span>
          </div>

          {/* Acciones */}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleViewDetails}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              Ver Detalles
            </Button>
            <Button
              onClick={() => router.push(`/agents/${agent.id}/upload`)}
              size="sm"
              className="flex-1"
            >
              Subir Archivo
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
