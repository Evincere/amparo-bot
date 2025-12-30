"""
Servicio principal de chat que orquesta la lógica de conversación.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import app.agents.agent_router as router_module
from app.config import settings
import redis
import json
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class ChatService:
    """Servicio que gestiona las conversaciones del chatbot."""
    
    def __init__(self):
        # Inicializar Redis (con fallback simple)
        self.use_redis = False
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis.ping() # Verificar conexión real
            self.use_redis = True
        except Exception as e:
            logger.warning(f"Redis no disponible, usando memoria local: {e}")
            self.redis = None
            self.local_history = {} # Fallback en memoria
        
        # Inicializar RAG (opcional - puede fallar si embeddings no están disponibles)
        self.use_rag = False
        try:
            if settings.knowledge_file:
                rag_service.ingest_knowledge(settings.knowledge_file)
                self.use_rag = True
                logger.info("RAG inicializado correctamente")
        except Exception as e:
            logger.warning(f"RAG no disponible (embeddings deshabilitados en cloud): {e}")
            self.use_rag = False
             
    def _get_redis_key(self, session_id: str) -> str:
        return f"chat:history:{session_id}"
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Obtiene el historial de una sesión."""
        if not self.use_redis:
            return self.local_history.get(session_id, [])
            
        try:
            history_json = self.redis.lrange(self._get_redis_key(session_id), 0, -1)
            # Redis guarda en orden inverso (LPUSH), así que invertimos para tener cronológico
            return [json.loads(msg) for msg in reversed(history_json)]
        except Exception as e:
            logger.error(f"Error recuperando historial Redis: {e}")
            return []
    
    def add_message_to_history(self, session_id: str, role: str, content: str):
        """Agrega un mensaje al historial."""
        msg = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.use_redis:
            if session_id not in self.local_history:
                self.local_history[session_id] = []
            self.local_history[session_id].append(msg)
            # Trim local history
            if len(self.local_history[session_id]) > 20:
                 self.local_history[session_id].pop(0)
            return

        try:
            key = self._get_redis_key(session_id)
            # Usamos LPUSH para agregar al inicio (luego invertimos al leer)
            self.redis.lpush(key, json.dumps(msg))
            # Mantener solo los últimos 20 mensajes
            self.redis.ltrim(key, 0, 19)
            # Configurar expiración
            self.redis.expire(key, settings.session_timeout)
        except Exception as e:
            logger.error(f"Error guardando en Redis: {e}")
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        agent_name: Optional[str] = None
    ) -> Dict:
        """
        Procesa un mensaje del usuario y retorna la respuesta.
        """
        print(f"DEBUG: chat_service.process_message iniciado. Msg: {message}", flush=True)
        try:
            # Obtener historial
            history = self.get_session_history(session_id)
            
            # Verificar router
            if router_module.agent_router is None:
                raise Exception("CRITICAL: Agent Router no inicializado (es None). Revisar main.py")

            # Clasificar y obtener agente apropiado
            if agent_name:
                agent = router_module.agent_router.get_agent(agent_name)
                fuero = agent_name
            else:
                agent, fuero = router_module.agent_router.get_agent_for_query(message)
            
            # Generar respuesta usando el mensaje original (el agente hará RAG internamente)
            response = await agent.generate_response(message, history)
            
            # Serializar si es objeto estructurado (compatibilidad hacia atras)
            final_response = response
            if hasattr(response, 'model_dump_json'):
                 final_response = response.model_dump_json()
            
            # Guardar en historial
            self.add_message_to_history(session_id, 'user', message)
            self.add_message_to_history(session_id, 'assistant', final_response)
            
            return {
                "response": final_response,
                "agent": fuero,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            
            # DEBUG: Log a archivo
            with open("service_debug.log", "a") as f:
                 f.write(f"TIMESTAMP: {datetime.now()}\n")
                 f.write(f"ERROR: {str(e)}\n")
                 import traceback
                 f.write(traceback.format_exc() + "\n")
                 f.write("-" * 50 + "\n")

            return {
                "response": self._get_error_response(),
                "agent": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def process_message_stream(
        self,
        message: str,
        session_id: str,
        agent_name: Optional[str] = None
    ):
        """
        Procesa un mensaje con streaming de respuesta.
        Genera chunks de respuesta en tiempo real.
        """
        try:
            history = self.get_session_history(session_id)
            
            if router_module.agent_router is None:
                raise Exception("CRITICAL: Agent Router no inicializado (es None)")
            
            # Clasificar y obtener agente
            if agent_name:
                agent = router_module.agent_router.get_agent(agent_name)
                fuero = agent_name
            else:
                agent, fuero = router_module.agent_router.get_agent_for_query(message)
            
            # Enviar metadata inicial
            yield {
                "type": "metadata",
                "agent": fuero,
                "session_id": session_id
            }
            
            # Streaming de respuesta
            full_response = ""
            async for chunk in agent.generate_response_stream(message, history):
                content_payload = chunk
                
                # DEBUG
                # logger.info(f"Chunk type: {type(chunk)}")
                
                # Manejar objetos serializables (AgentResponse)
                if hasattr(chunk, 'model_dump_json'):
                    chunk_str = chunk.model_dump_json()
                    content_payload = chunk.model_dump() # Enviar como dict al frontend
                elif isinstance(chunk, dict):
                     chunk_str = str(chunk) # Fallback simple (esto puede ser el problema si es dict)
                else:
                    chunk_str = str(chunk)
                
                full_response += chunk_str
                yield {
                    "type": "content",
                    "content": content_payload
                }
            
            # Guardar en historial
            self.add_message_to_history(session_id, 'user', message)
            self.add_message_to_history(session_id, 'assistant', full_response)
            
            # Finalizar
            yield {
                "type": "end",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            with open("service_debug.log", "a") as f:
                 f.write(f"TIMESTAMP: {datetime.now()} [STREAM]\n")
                 f.write(f"ERROR: {str(e)}\n")
                 import traceback
                 f.write(traceback.format_exc() + "\n")
            
            yield {
                "type": "error",
                "error": str(e),
                "message": self._get_error_response()
            }
    
    def clear_session(self, session_id: str):
        """Limpia el historial de una sesión."""
        if not self.use_redis:
            if session_id in self.local_history:
                del self.local_history[session_id]
            return

        try:
            self.redis.delete(self._get_redis_key(session_id))
            logger.info(f"Sesión {session_id} limpiada")
        except Exception as e:
             logger.error(f"Error limpiando sesión Redis: {e}")
    
    def get_session_count(self) -> int:
        """Retorna el número de sesiones activas (aprox)."""
        if not self.use_redis:
            return len(self.local_history)
            
        try:
            return len(self.redis.keys("chat:history:*"))
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            return 0
    
    def _get_error_response(self) -> str:
        """Respuesta de error genérica."""
        return (
            "Disculpa, estoy experimentando dificultades técnicas. "
            "Por favor, intenta nuevamente en unos momentos o contacta "
            "directamente a la Defensa Pública al 0800-555-JUSTICIA."
        )


# Instancia global
chat_service = ChatService()
