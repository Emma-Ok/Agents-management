// Layout principal de la aplicación
'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header/Navigation */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo y título */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-black rounded-md flex items-center justify-center">
                <span className="text-white font-bold text-sm">🤖</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">
                AI Agent Manager
              </span>
            </div>

            {/* Navegación principal */}
            <nav className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="bg-black text-white hover:bg-gray-800 px-4"
              >
                <span className="mr-2">🤖</span>
                Agents
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <span className="mr-2">⚙️</span>
                Settings
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <span className="mr-2">❓</span>
                Help
              </Button>
            </nav>

            {/* Botón de modo oscuro */}
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                className="w-9 h-9 p-0"
              >
                <span className="text-lg">🌙</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
