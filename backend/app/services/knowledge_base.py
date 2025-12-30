"""
Servicio para gestionar la base de conocimiento desde JSON.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Servicio para cargar y consultar la base de conocimiento."""
    
    def __init__(self, knowledge_file: str):
        self.knowledge_file = Path(knowledge_file)
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Carga el JSON de conocimiento."""
        try:
            if not self.knowledge_file.exists():
                logger.warning(f"Archivo de conocimiento no encontrado: {self.knowledge_file}")
                self.data = {"documents": []}
                return
            
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            logger.info(f"Base de conocimiento cargada exitosamente: {len(self.data.get('documents', []))} documentos")
        
        except Exception as e:
            logger.error(f"Error al cargar base de conocimiento: {e}")
            self.data = {"documents": []}

    def reload(self):
        self.load()
    
    def _filter_documents(self, tag: str = None, section: str = None) -> List[Dict]:
        """Filtra documentos por tag o sección."""
        docs = self.data.get("documents", [])
        filtered = []
        for doc in docs:
            if tag and tag not in doc.get("tags", []):
                continue
            if section and doc.get("seccion") != section:
                continue
            filtered.append(doc)
        return filtered

    def get_general_info(self) -> Dict[str, Any]:
        """Obtiene información general institucional construida desde documentos."""
        # Construimos un dict similar al anterior buscando docs clave
        info = {"institucional": {}, "contacto": {}}
        
        inst_docs = self._filter_documents(section="institucional")
        if inst_docs:
            info["institucional"]["descripcion"] = inst_docs[0].get("contenido", "")
        
        contact_docs = self._filter_documents(section="contacto")
        for doc in contact_docs:
            if "sede-central" in doc.get("tags", []):
                info["contacto"]["direccion"] = doc.get("contenido")
        
        return info
    
    def get_fuero_info(self, fuero: str) -> Optional[Dict[str, Any]]:
        """
        Simula la estructura antigua de fuero recuperando documentos relevantes.
        Mapea nombres de fuero internos a tags del dataset.
        """
        # Mapeo de nombres internos a tags de búsqueda
        tag_map = {
            "civil": "civil",
            "familia": "familia",
            "penal": "penal", # Ojo: puede traer penal juvenil también si no filtramos
            "penal_juvenil": "penal-juvenil",
            "nna_pcr": "NNA" # O "nna_pcr" si agregamos ese tag específico
        }
        
        search_tag = tag_map.get(fuero, fuero)
        
        # Buscar documentos del fuero
        docs = self._filter_documents(tag=search_tag)
        if not docs:
            return None
        
        # Construir objeto simulado
        # Usamos el primer documento como "descripcion main"
        main_doc = docs[0]
        
        # Recolectar todas las keywords de todos los docs del fuero
        all_keywords = set()
        for doc in docs:
            all_keywords.update(doc.get("tags", []))
            
        return {
            "nombre": main_doc.get("titulo", f"Fuero {fuero}"),
            "descripcion": main_doc.get("contenido", ""),
            "keywords": list(all_keywords),
            "tramites": [{"nombre": d.get("titulo"), "descripcion": d.get("contenido")} for d in docs]
        }
    
    def get_fuero_keywords(self, fuero: str) -> List[str]:
        """Obtiene keywords para routing."""
        info = self.get_fuero_info(fuero)
        if info:
            return info.get("keywords", [])
        return []
    
    def get_all_fueros(self) -> List[str]:
        """Lista fueros soportados (hardcoded porque ahora es dinámico)."""
        return ["civil", "familia", "penal", "penal_juvenil", "nna_pcr"]
    
    def search_faqs(self, fuero: Optional[str], query: str) -> List[Dict[str, Any]]:
        """Busca en documentos tipo pregunta_respuesta."""
        results = []
        # Buscar en todos los docs tipo 'pregunta_respuesta'
        # Esto es una búsqueda muy básica, RAG es mejor, pero mantenemos compatibilidad
        query_lower = query.lower()
        docs = self.data.get("documents", [])
        
        for doc in docs:
            if doc.get("tipo") == "pregunta_respuesta":
                # Si se especifica fuero, filtrar por tags
                if fuero and fuero != "general":
                    # Mapeo simple: si el fuero está en los tags
                    # Esto es aproximado
                    pass 
                
                if query_lower in doc.get("titulo", "").lower() or query_lower in doc.get("contenido", "").lower():
                    results.append({
                        "pregunta": doc.get("titulo"),
                        "respuesta": doc.get("contenido")
                    })
        return results

    def get_context_for_fuero(self, fuero: str) -> str:
        """Genera contexto textual concatenando documentos del fuero."""
        info = self.get_fuero_info(fuero)
        if not info:
            return ""
        
        lines = [f"Contexto para fuero {fuero}:"]
        lines.append(f"Descripción: {info.get('descripcion')}")
        
        for tramite in info.get("tramites", []):
             lines.append(f"- {tramite['nombre']}: {tramite['descripcion']}")
             
        return "\n".join(lines)

    def get_general_context(self) -> str:
        """Contexto general."""
        docs = self._filter_documents(section="institucional") + self._filter_documents(section="contacto")
        return "\n".join([f"{d.get('titulo')}: {d.get('contenido')}" for d in docs])

    def _get_default_knowledge(self):
        return {"documents": []}


# Instancia global (se inicializará en main.py)
knowledge_service: Optional[KnowledgeBaseService] = None
