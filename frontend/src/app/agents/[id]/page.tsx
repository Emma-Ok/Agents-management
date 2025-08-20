'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAgent } from '@/hooks/useAgents';
import { useDocuments, useDeleteDocumentMutation } from '@/hooks/useDocuments';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { MainLayout } from '@/components/layout/MainLayout';
import { UploadDocumentModal } from '@/components/documents/UploadDocumentModal';
import { EditAgentModal } from '@/components/agents/EditAgentModal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useUpdateAgentMutation } from '@/hooks/useAgents';
import { formatFileSize } from '@/lib/utils';

export default function AgentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params.id as string;
  
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [deleteDocumentId, setDeleteDocumentId] = useState<string | null>(null);
  
  const { agent, loading: agentLoading, refetch: refetchAgent } = useAgent(agentId);
  const { documents, isLoading: documentsLoading, refetch: refetchDocuments } = useDocuments(agentId);
  const updateAgentMutation = useUpdateAgentMutation();
  const deleteDocumentMutation = useDeleteDocumentMutation();

  if (agentLoading.isLoading || documentsLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading agent...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (agentLoading.error || !agent) {
    return (
      <MainLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="text-center text-red-700">
            <h3 className="text-lg font-semibold mb-2">Agent not found</h3>
            <p>{agentLoading.error || 'The requested agent could not be found.'}</p>
            <Button 
              onClick={() => router.push('/dashboard')}
              className="mt-4"
              variant="outline"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Calcular estadísticas de documentos
  const totalSize = documents.reduce((sum, doc) => sum + doc.file_size, 0);
  const avgSize = documents.length > 0 ? totalSize / documents.length : 0;

  // Funciones de manejo
  const handleUploadComplete = () => {
    refetchDocuments();
    refetchAgent();
  };

  const handleDeleteDocument = (documentId: string) => {
    setDeleteDocumentId(documentId);
  };

  const handleConfirmDeleteDocument = () => {
    if (deleteDocumentId) {
      deleteDocumentMutation.mutate(deleteDocumentId);
      setDeleteDocumentId(null);
    }
  };

  return (
    <MainLayout>
      {/* Header con navegación */}
      <div className="flex items-center gap-4 mb-8">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard')}
          className="text-gray-600 hover:text-gray-900"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Agents
        </Button>
        
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900">
            {agent.name}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Upload Files
          </Button>
          <Button
            onClick={() => setIsEditModalOpen(true)}
            className="flex items-center gap-2 bg-black hover:bg-gray-800 text-white"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Agent
          </Button>
        </div>
      </div>

      {/* Agent Configuration Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Agent Configuration</CardTitle>
          <p className="text-sm text-gray-600">
            The system prompt and configuration for this agent
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Name</h4>
            <p className="text-gray-700">{agent.name}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">System Prompt</h4>
            <p className="text-gray-700 leading-relaxed">
              {agent.prompt}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agent.documents_count}</div>
            <p className="text-xs text-gray-500">Files in knowledge base</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatFileSize(totalSize)}</div>
            <p className="text-xs text-gray-500">Avg. {formatFileSize(avgSize)} per file</p>
          </CardContent>
        </Card>
      </div>

      {/* Documents Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Knowledge Base Documents</CardTitle>
          <p className="text-sm text-gray-600">
            Documents uploaded to this agent&apos;s knowledge base
          </p>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                No documents yet
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Upload documents to build this agent&apos;s knowledge base.
              </p>
              <Button 
                onClick={() => setIsUploadModalOpen(true)}
                className="bg-black hover:bg-gray-800 text-white"
              >
                Upload First Document
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((document) => (
                <div 
                  key={document.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{document.filename}</p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(document.file_size)} • {document.document_type.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open(document.file_url, '_blank')}
                      className="text-gray-600 hover:text-blue-600"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteDocument(document.id)}
                      className="text-gray-600 hover:text-red-600"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Modal */}
      <UploadDocumentModal
        isOpen={isUploadModalOpen}
        agentId={agentId}
        agentName={agent.name}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />

      {/* Edit Agent Modal */}
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

      {/* Delete Document Confirmation */}
      <ConfirmDialog
        isOpen={deleteDocumentId !== null}
        title="Delete Document"
        message="Are you sure you want to delete this document? This action cannot be undone."
        confirmText="Delete Document"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteDocumentMutation.isPending}
        onConfirm={handleConfirmDeleteDocument}
        onCancel={() => setDeleteDocumentId(null)}
      />
    </MainLayout>
  );
}
