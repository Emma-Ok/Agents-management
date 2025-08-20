// Error Boundary para capturar errores en React y mostrar UI de fallback
'use client';

import React, { Component, ReactNode } from 'react';
import { Button } from './Button';
import { Card, CardContent, CardHeader, CardTitle } from './Card';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Actualiza el estado para que la siguiente renderización muestre la UI de fallback
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Registra el error
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Llamar callback personalizado si existe
    this.props.onError?.(error, errorInfo);
  }

  handleReload = () => {
    // Recargar la página
    window.location.reload();
  };

  handleReset = () => {
    // Resetear el estado del error boundary
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      // Si se proporciona un fallback personalizado, usarlo
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // UI de fallback por defecto
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="max-w-lg w-full">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <CardTitle className="text-xl text-gray-900">¡Oops! Algo salió mal</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <p className="text-gray-600">
                Ha ocurrido un error inesperado en la aplicación. Esto puede deberse a un problema temporal.
              </p>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="text-left bg-red-50 p-4 rounded-lg border border-red-200">
                  <summary className="text-sm font-medium text-red-800 cursor-pointer">
                    Detalles del error (desarrollo)
                  </summary>
                  <div className="mt-2 text-xs text-red-700 font-mono">
                    <p><strong>Error:</strong> {this.state.error.message}</p>
                    <p><strong>Stack:</strong></p>
                    <pre className="mt-1 overflow-auto max-h-32 text-xs">
                      {this.state.error.stack}
                    </pre>
                    {this.state.errorInfo && (
                      <>
                        <p className="mt-2"><strong>Component Stack:</strong></p>
                        <pre className="mt-1 overflow-auto max-h-32 text-xs">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </>
                    )}
                  </div>
                </details>
              )}
              
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={this.handleReset}
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  Intentar de nuevo
                </Button>
                <Button
                  onClick={this.handleReload}
                  className="w-full sm:w-auto bg-black hover:bg-gray-800 text-white"
                >
                  Recargar página
                </Button>
              </div>
              
              <p className="text-xs text-gray-500 mt-4">
                Si el problema persiste, contacta al soporte técnico.
              </p>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Hook para reportar errores de manera programática
 */
export function useErrorHandler() {
  const reportError = (error: Error, context?: string) => {
    console.error(`Error reported${context ? ` in ${context}` : ''}:`, error);
    
    // Aquí podrías enviar el error a un servicio de monitoreo
    // como Sentry, LogRocket, etc.
  };

  return { reportError };
}

/**
 * Componente de error más simple para casos específicos
 */
interface SimpleErrorProps {
  error: Error | string;
  onRetry?: () => void;
  onReset?: () => void;
}

export function SimpleError({ error, onRetry, onReset }: SimpleErrorProps) {
  const errorMessage = typeof error === 'string' ? error : error.message;
  
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 className="text-sm font-medium text-red-800 mb-2">
        Error
      </h3>
      <p className="text-sm text-red-700 mb-4">
        {errorMessage}
      </p>
      <div className="flex gap-2 justify-center">
        {onRetry && (
          <Button
            onClick={onRetry}
            size="sm"
            variant="outline"
          >
            Reintentar
          </Button>
        )}
        {onReset && (
          <Button
            onClick={onReset}
            size="sm"
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            Cancelar
          </Button>
        )}
      </div>
    </div>
  );
}
