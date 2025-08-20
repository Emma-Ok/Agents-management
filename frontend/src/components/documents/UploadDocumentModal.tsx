// Modal para upload de documentos
'use client';

import React from 'react';
import { DocumentUpload } from './DocumentUpload';

interface UploadDocumentModalProps {
  isOpen: boolean;
  agentId: string;
  agentName: string;
  onClose: () => void;
  onUploadComplete?: () => void;
}

export function UploadDocumentModal({ 
  isOpen, 
  agentId, 
  agentName, 
  onClose, 
  onUploadComplete 
}: UploadDocumentModalProps) {
  if (!isOpen) return null;

  const handleUploadComplete = () => {
    onUploadComplete?.();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Upload Files
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add documents to <span className="font-medium">{agentName}</span>&apos;s knowledge base
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Upload Component */}
        <div className="p-6">
          <DocumentUpload
            agentId={agentId}
            onUploadComplete={handleUploadComplete}
            onClose={onClose}
          />
        </div>
      </div>
    </div>
  );
}
