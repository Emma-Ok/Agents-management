#!/usr/bin/env python3
"""
Simple FastAPI startup script for testing the basic functionality
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a simple FastAPI app for testing
app = FastAPI(
    title="AI Agents Manager",
    version="1.0.0",
    description="AI Agents Manager - Gestión de agentes de IA y su base de conocimiento"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AI Agents Manager",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Agents Manager",
        "version": "1.0.0"
    }

@app.get("/api/v1/agents")
async def list_agents():
    """Temporary endpoint to list agents"""
    return {
        "agents": [],
        "total": 0,
        "message": "No agents found - database not connected yet"
    }

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
