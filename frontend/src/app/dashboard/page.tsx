'use client';

// Página principal del Dashboard - Basado en diseño Figma

import React from 'react';
import { useAgents } from '@/hooks/useAgents';
import { AgentCard } from '@/components/agents/AgentCard';
import { CreateAgentModal } from '@/components/agents/CreateAgentModal';
import { Button } from '@/components/ui/Button';
import { MainLayout } from '@/components/layout/MainLayout';

export default function DashboardPage() {
  const { agents, isLoading, isError, error, createAgent } = useAgents();
  const [isCreateModalOpen, setIsCreateModalOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');

  // Filtrar agentes por búsqueda
  const filteredAgents = agents.filter(agent => {
    if (!agent || !searchQuery.trim()) return true;
    
    const name = agent.name || '';
    const prompt = agent.prompt || '';
    const query = searchQuery.toLowerCase();
    
    return name.toLowerCase().includes(query) || 
           prompt.toLowerCase().includes(query);
  });

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading agents...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (isError) {
    return (
      <MainLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="text-center text-red-700">
            <h3 className="text-lg font-semibold mb-2">Error loading agents</h3>
            <p>{error?.message}</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">
              AI Agents
            </h1>
            <p className="text-gray-600">
              Manage your AI agents and their knowledge bases
            </p>
          </div>
          <Button 
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-black hover:bg-gray-800 text-white px-4 py-2"
          >
            <span className="mr-2">+</span>
            Create Agent
          </Button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <svg 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black focus:border-black transition-colors"
          />
        </div>
      </div>

      {/* Agents Grid */}
      {filteredAgents.length === 0 ? (
        <div className="text-center py-16">
          {agents.length === 0 ? (
            <>
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No agents yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-sm mx-auto">
                Create your first AI agent to start managing documents and building knowledge bases.
              </p>
              <Button 
                onClick={() => setIsCreateModalOpen(true)}
                className="bg-black hover:bg-gray-800 text-white"
              >
                Create First Agent
              </Button>
            </>
          ) : (
            <>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No agents found
              </h3>
              <p className="text-gray-600">
                No agents match your search criteria. Try adjusting your search.
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <AgentCard 
              key={agent.id} 
              agent={agent} 
            />
          ))}
        </div>
      )}

      {/* Create Agent Modal */}
      <CreateAgentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={async (data) => {
          const result = await createAgent(data);
          setIsCreateModalOpen(false);
          return result;
        }}
      />
    </MainLayout>
  );
}
