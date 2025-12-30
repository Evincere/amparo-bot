"""
Aplicación FastAPI principal del bot de consulta.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# CRITICAL: Apply SSL Bypass as early as possible
from app.utils.ssl_patch import apply_ssl_bypass
apply_ssl_bypass()

from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import uuid

from app.config import settings
import app.services.knowledge_base as kb_module
from app.services.knowledge_base import KnowledgeBaseService
import app.agents.agent_router as router_module
from app.agents.agent_router import AgentRouter
from app.services.chat_service import chat_service

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Defensa Mendoza - Bot de Consulta API",
    description="API para el bot de consulta inteligente de la Defensa Pública de Mendoza",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # settings.cors_origins_list, # Forzando * para evitar lios
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ===== Modelos de datos =====

class ChatMessage(BaseModel):
    """Mensaje de chat del usuario."""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: Optional[str] = Field(None, description="ID de sesión (se genera si no se provee)")
    agent: Optional[str] = Field(None, description="Agente específico a usar (opcional)")


class ChatResponse(BaseModel):
    """Respuesta del bot."""
    response: str
    agent: str
    session_id: str
    timestamp: str


# ===== Inicialización =====

@app.on_event("startup")
async def startup_event():
    """Inicializa servicios al arrancar la aplicación."""
    logger.info("Iniciando aplicación...")
    logger.info(f"OLLAMA_HOST config: {settings.ollama_host}")
    
    # Inicializar knowledge base
    # IMPORTANTE: Asignar al módulo, no a variable local
    kb_module.knowledge_service = KnowledgeBaseService(settings.knowledge_file)
    logger.info("Knowledge base inicializado")
    
    # Inicializar router de agentes
    router_module.agent_router = AgentRouter(kb_module.knowledge_service)
    logger.info("Agent router inicializado")
    
    logger.info(f"Aplicación lista en {settings.host}:{settings.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup al cerrar la aplicación."""
    logger.info("Cerrando aplicación...")
    # Reload trigger


# ===== Endpoints =====

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bot de Consulta - Defensa Pública de Mendoza",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "knowledge_base": "loaded" if knowledge_service else "not loaded",
        "agents": "ready" if agent_router else "not ready",
        "active_sessions": chat_service.get_session_count()
    }


@app.get("/api/fueros")
async def list_fueros():
    """Lista todos los fueros disponibles."""
    if not agent_router:
        raise HTTPException(status_code=503, detail="Servicio no disponible")
    
    agents_info = agent_router.get_all_agents_info()
    
    return {
        "fueros": [
            {
                "id": fuero,
                "name": info["fuero"],
                "keywords_count": len(info["keywords"])
            }
            for fuero, info in agents_info.items()
        ]
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    """
    Endpoint principal de chat.
    Recibe un mensaje y retorna la respuesta del agente apropiado.
    """
    print(f"DEBUG: Request recibido en /api/chat: {msg}", flush=True)
    try:
        # Generar session_id si no se provee
        session_id = msg.session_id or str(uuid.uuid4())
        
        # Procesar mensaje
        result = await chat_service.process_message(
            message=msg.message,
            session_id=session_id,
            agent_name=msg.agent
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        logger.error(f"Error en endpoint /api/chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/api/chat/stream")
async def chat_stream(msg: ChatMessage):
    """
    Endpoint de chat con streaming.
    Retorna la respuesta en chunks para mejor UX.
    """
    try:
        # Generar session_id si no se provee
        session_id = msg.session_id or str(uuid.uuid4())
        
        async def generate():
            """Generador para SSE (Server-Sent Events)."""
            async for chunk in chat_service.process_message_stream(
                message=msg.message,
                session_id=session_id,
                agent_name=msg.agent
            ):
                # Formatear como SSE
                import json
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        logger.error(f"Error en endpoint /api/chat/stream: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Limpia el historial de una sesión."""
    chat_service.clear_session(session_id)
    return {"message": "Sesión limpiada", "session_id": session_id}


@app.post("/api/admin/reload")
async def reload_knowledge(api_key: str):
    """
    Endpoint administrativo para recargar la base de conocimiento.
    Requiere API key de administración.
    """
    if not settings.admin_api_key or api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    knowledge_service.reload()
    return {"message": "Base de conocimiento recargada", "timestamp": "now"}


# ===== Error handlers =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para excepciones HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para excepciones generales."""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor"}
    )


# ===== Main =====

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
