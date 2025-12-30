import asyncio
import logging
import os
from dotenv import load_dotenv

# Setup básico
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Importar dependencias del proyecto
from app.config import settings
from app.services.knowledge_base import KnowledgeBaseService
from app.agents.graph_agent import GraphAgent

async def test_graph():
    print("--- INICIANDO TEST LANGGRAPH ---")
    
    # 1. Cargar KB
    kb = KnowledgeBaseService(settings.knowledge_file)
    print(f"✅ KB Cargada.")
    
    # 2. Inicializar Agente
    # Asegurarnos de usar el modelo definido en settings
    print(f"🤖 Modelo configurado: {settings.ollama_model}")
    agent = GraphAgent(kb, model_name=settings.ollama_model)
    
    query = "Donde queda la defensoria y que horarios tienen?"
    print(f"\n❓ Pregunta: {query}")
    print("\n--- STREAMING EVENTS ---")
    
    final_answer = ""
    
    # 3. Ejecutar y stremear
    # 3. Ejecutar (Invoke para debug)
    try:
        inputs = {"input": query, "chat_history": []}
        result = await agent.graph.ainvoke(inputs)
        
        print(f"\n✅ Ejecución finalizada.")
        print(f"Result keys: {result.keys()}")
        
        if "answer" in result:
            ans = result["answer"]
            if hasattr(ans, 'components'):
                print(f"Respuesta Estructurada: {ans.components}")
            else:
                print(f"Respuesta Final: {ans}")
                    
    except Exception:
        import traceback
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        traceback.print_exc()
        
    print("\n--- RESULTADO FINAL ---")
    print(final_answer)

if __name__ == "__main__":
    asyncio.run(test_graph())
