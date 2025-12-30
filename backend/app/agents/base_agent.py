"""
Clase base abstracta para todos los agentes especializados.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from ollama import Client

from app.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Clase base para agentes especializados."""
    
    def __init__(self, fuero_name: str, knowledge_service):
        self.fuero_name = fuero_name
        self.knowledge_service = knowledge_service
        # No inicializamos cliente aquí, usamos httpx en request
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Retorna el prompt de sistema específico del agente.
        Debe ser implementado por cada agente especializado.
        """
        pass
    
    def get_keywords(self) -> List[str]:
        """
        Retorna las keywords que identifican este agente.
        Obtenidas dinámicamente de la base de conocimiento.
        """
        return self.knowledge_service.get_fuero_keywords(self.fuero_name)
    
    def get_context(self) -> str:
        """Obtiene el contexto del fuero desde la knowledge base."""
        if self.fuero_name == "general":
            return self.knowledge_service.get_general_context()
        return self.knowledge_service.get_context_for_fuero(self.fuero_name)
    
    def format_messages(self, user_message: str, history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Formatea los mensajes para la API de Ollama."""
        messages = []
        
        # System prompt con contexto
        system_content = self.get_system_prompt()
        context = self.get_context()
        if context:
            system_content += f"\n\nContexto específico:\n{context}"
        
        messages.append({
            'role': 'system',
            'content': system_content
        })
        
        # Historial de conversación (si existe)
        if history:
            for msg in history[-10:]:  # Últimos 10 mensajes
                messages.append(msg)
        
        # Mensaje actual del usuario
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        return messages
    
    async def generate_response(self, user_message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Genera una respuesta usando request directo a Ollama (requests/httpx).
        """
        import httpx
        try:
            print(f"DEBUG: BaseAgent.generate_response iniciado. httpx importado? {'httpx' in locals()}", flush=True)
            messages = self.format_messages(user_message, history)
            
            logger.info(f"[{self.fuero_name}] Generando respuesta para: {user_message[:50]}...")
            
            url = f"{settings.ollama_host}/api/chat"
            payload = {
                "model": settings.ollama_model,
                "messages": messages,
                "stream": False
            }
            
            headers = {'Authorization': f'Bearer {settings.ollama_api_key}'}
            
            async with httpx.AsyncClient(verify=settings.ssl_verify) as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                
            answer = data['message']['content']
            logger.info(f"[{self.fuero_name}] Respuesta generada exitosamente")
            
            return answer
        
        except Exception as e:
            logger.error(f"Error al generar respuesta: {e}")
            # DEBUG CAMPO: Escribir error a archivo para ver qué pasa
            with open("debug_error.log", "a") as f:
                f.write(f"Error en generate_response: {str(e)}\nImport error? {'httpx' not in locals()}\n")
                import traceback
                f.write(traceback.format_exc() + "\n")
            
            return self._get_fallback_response()
    
    async def generate_response_stream(self, user_message: str, history: List[Dict[str, str]] = None):
        """
        Genera una respuesta con streaming usando httpx directo.
        """
        import httpx
        import json
        try:
            messages = self.format_messages(user_message, history)
            
            logger.info(f"[{self.fuero_name}] Generando respuesta streaming para: {user_message[:50]}...")
            
            url = f"{settings.ollama_host}/api/chat"
            payload = {
                "model": settings.ollama_model,
                "messages": messages,
                "stream": True
            }
            
            headers = {'Authorization': f'Bearer {settings.ollama_api_key}'}
            
            async with httpx.AsyncClient(verify=settings.ssl_verify) as client:
                async with client.stream('POST', url, json=payload, headers=headers, timeout=60.0) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if 'message' in data and 'content' in data['message']:
                                    yield data['message']['content']
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
        
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            yield self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Respuesta de fallback en caso de error."""
        return (
            "Disculpa, estoy teniendo dificultades técnicas en este momento. "
            "Por favor, contacta directamente a la Defensa Pública al 0800-555-JUSTICIA "
            "o visita https://defensamendoza.gob.ar"
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Información del agente para debugging."""
        return {
            "fuero": self.fuero_name,
            "keywords": self.get_keywords(),
            "model": settings.ollama_model
        }
