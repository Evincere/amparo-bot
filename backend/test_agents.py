import asyncio
import os
from dotenv import load_dotenv

# Cargar envs (backend/.env)
load_dotenv()

from app.config import settings
from app.services.knowledge_base import KnowledgeBaseService
from app.agents.agent_router import AgentRouter
from app.agents.general_agent import GeneralAgent

async def test():
    print("--- INICIANDO TEST DE INTEGRACIÓN ---")
    
    # 1. Verificar Carga de Conocimiento
    kb = KnowledgeBaseService(settings.knowledge_file)
    print(f"✅ KB Cargada. Institución: {kb.data.get('general', {}).get('institucional', {}).get('nombre')}")
    
    # 2. Verificar Router (Lógica local, no requiere LLM)
    router = AgentRouter(kb)
    print("\n--- TEST ROUTING ---")
    
    test_queries = [
        ("Me quiero divorciar", "familia"),
        ("Tengo una deuda con una tarjeta", "civil"),
        ("Tengo un pariente detenido en la carcel", "penal"),
        ("Donde queda la defensoria?", "general"),
        ("Quiero adoptar un niño", "nna_pcr") 
    ]
    
    for query, expected in test_queries:
        # Usamos classify_query que es sincrono
        agent_key = router.classify_query(query)
        result = "✅" if agent_key == expected else f"❌ Esp: {expected}"
        print(f"Query: '{query}' -> Agente: {agent_key} {result}")

    # 3. Verificar Conexión LLM (Si hay API Key)
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        print(f"\n--- TEST OLLAMA CLOUD (Key: {api_key[:5]}...) ---")
        agent = GeneralAgent(kb)
        
        # Inyectar contexto manual para test
        context = kb.get_general_context()
        
        user_msg = "Hola, ¿cuál es el número de teléfono?"
        print(f"Propmteando con: '{user_msg}'...")
        
        try:
            # Usamos el metodo generate_response en modo streaming
            response_stream = agent.generate_response_stream(
                user_message=user_msg,
                history=[]
            )
            
            print("Respuesta LLM: ", end="")
            full_response = ""
            async for chunk in response_stream:
                token = chunk
                if isinstance(chunk, dict): # Caso estructurado o metadata
                     token = str(chunk)
                print(token, end="", flush=True)
                full_response += str(chunk)
            print("\n\n✅ Conexión con Ollama exitosa!")
        except Exception as e:
            print(f"\n❌ Error conectando a Ollama: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️ OLLAMA_API_KEY no encontrada en .env, saltando test LLM.")

if __name__ == "__main__":
    asyncio.run(test())
