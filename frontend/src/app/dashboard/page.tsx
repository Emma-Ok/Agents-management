'use client';

// Página principal del Dashboard

import React from 'react';
import { useAgents } from '@/hooks/useAgents';
import { AgentCard } from '@/components/agents/AgentCard';
import { CreateAgentModal } from '@/components/agents/CreateAgentModal';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function DashboardPage() {
  const { agents, loading, createAgent } = useAgents();
  const [isCreateModalOpen, setIsCreateModalOpen] = React.useState(false);

  if (loading.isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando agentes...</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading.error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="text-center text-red-700">
              <h3 className="text-lg font-semibold mb-2">Error al cargar agentes</h3>
              <p>{loading.error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Dashboard de Agentes IA
          </h1>
          <p className="text-gray-600 mt-2">
            Gestiona tus agentes de inteligencia artificial y sus documentos
          </p>
        </div>
        <Button 
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Crear Agente
        </Button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Agentes</CardTitle>
            <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agents.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documentos Totales</CardTitle>
            <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.reduce((total, agent) => total + agent.documents_count, 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Agente Más Activo</CardTitle>
            <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.length > 0 
                ? agents.reduce((prev, current) => 
                    prev.documents_count > current.documents_count ? prev : current
                  ).name.substring(0, 15) + (agents.reduce((prev, current) => 
                    prev.documents_count > current.documents_count ? prev : current
                  ).name.length > 15 ? '...' : '')
                : 'N/A'
              }
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Agentes */}
      {agents.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <svg 
                className="mx-auto h-12 w-12 text-gray-400" 
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
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No hay agentes creados
              </h3>
              <p className="mt-2 text-gray-600">
                Comienza creando tu primer agente de IA para gestionar documentos.
              </p>
              <Button 
                onClick={() => setIsCreateModalOpen(true)}
                className="mt-4"
              >
                Crear Primer Agente
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard 
              key={agent.id} 
              agent={agent} 
            />
          ))}
        </div>
      )}

      {/* Modal de Crear Agente */}
      <CreateAgentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={createAgent}
      />
    </div>
  );
}
