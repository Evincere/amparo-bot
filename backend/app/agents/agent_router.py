"""
Router inteligente que determina qué agente debe responder.
"""
import logging
from typing import Optional, Dict
# from app.agents.general_agent import GeneralAgent
from app.agents.graph_agent import GraphAgent
# Las clases legacy ya no se usan
# from app.agents.civil_agent import CivilAgent
# from app.agents.familia_agent import FamiliaAgent
# from app.agents.penal_agent import PenalAgent
# from app.agents.penal_juvenil_agent import PenalJuvenilAgent
# from app.agents.nna_pcr_agent import NNAPCRAgent

logger = logging.getLogger(__name__)


class AgentRouter:
    """Router que clasifica consultas y deriva al agente apropiado."""
    
    def __init__(self, knowledge_service):
        # Inicializar todos los agentes usando GraphAgent universal
        self.agents = {
            "general": GraphAgent(knowledge_service, fuero_name="general"),
            "civil": GraphAgent(knowledge_service, fuero_name="civil"),
            "familia": GraphAgent(knowledge_service, fuero_name="familia"),
            "penal": GraphAgent(knowledge_service, fuero_name="penal"),
            "penal_juvenil": GraphAgent(knowledge_service, fuero_name="penal_juvenil"),
            "nna_pcr": GraphAgent(knowledge_service, fuero_name="nna_pcr")
        }
        
        # Ya no necesitamos importar los agentes legacy si no se usan
        logger.info(f"Router inicializado con {len(self.agents)} agentes (GraphAgent)")
    
    def classify_query(self, message: str) -> str:
        """
        Clasifica la consulta y retorna el nombre del agente apropiado.
        
        Usa un sistema simple de keyword matching con scoring.
        """
        message_lower = message.lower()
        scores = {fuero: 0 for fuero in self.agents.keys()}
        
        # Calcular score para cada agente basado en keywords
        for fuero, agent in self.agents.items():
            keywords = agent.get_keywords()
            for keyword in keywords:
                if keyword in message_lower:
                    # Keywords más largas tienen más peso
                    weight = len(keyword.split())
                    scores[fuero] += weight
        
        # Obtener el agente con mayor score
        max_score = max(scores.values())
        
        # Si no hay match claro, usar agente general
        if max_score == 0:
            logger.info(f"Sin match de keywords, usando agente general")
            return "general"
        
        # Obtener agente con mayor score
        best_agent = max(scores.items(), key=lambda x: x[1])[0]
        
        logger.info(f"Clasificación: '{message[:50]}...' -> {best_agent} (score: {scores[best_agent]})")
        logger.debug(f"Scores: {scores}")
        
        return best_agent
    
    def get_agent(self, fuero: str):
        """Obtiene un agente por nombre de fuero."""
        return self.agents.get(fuero, self.agents["general"])
    
    def get_agent_for_query(self, message: str):
        """Clasifica y retorna el agente apropiado para la consulta."""
        fuero = self.classify_query(message)
        return self.get_agent(fuero), fuero
    
    def get_all_agents_info(self) -> Dict:
        """Retorna información de todos los agentes (para debugging)."""
        return {
            fuero: agent.get_agent_info()
            for fuero, agent in self.agents.items()
        }


# Instancia global (se inicializará en main.py)
agent_router: Optional[AgentRouter] = None
