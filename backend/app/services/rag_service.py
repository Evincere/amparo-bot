"""
Servicio RAG (Retrieval-Augmented Generation) para búsqueda semántica.
"""
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Gestiona la indexación y recuperación de conocimiento."""

    def __init__(self):
        print(f"DEBUG: RAG config - Provider: {settings.embedding_provider}, Model: {settings.embedding_model}")
        
        # Use HuggingFace embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"HuggingFaceEmbeddings inicializado con modelo: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Error inicializando HuggingFaceEmbeddings: {e}")
            # Fallback a None o error crítico según necesidad
            self.embeddings = None

        self.persist_directory = "data/chroma_db"
        self.vector_store = None
        
        if self.embeddings:
            self._initialize_db()

    def _initialize_db(self):
        """Inicializa o carga la base de datos vectorial."""
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="defensa_mendoza"
            )
            logger.info("ChromaDB inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {e}")

    def ingest_knowledge(self, knowledge_file: str):
        """Ingesta el archivo knowledge.json en la base vectorial."""
        try:
            path = Path(knowledge_file)
            if not path.exists():
                logger.error(f"Archivo de conocimiento no encontrado: {knowledge_file}")
                return

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            documents = []
            raw_docs = data.get("documents", [])
            
            logger.info(f"Procesando {len(raw_docs)} documentos para ingesta...")

            for doc in raw_docs:
                # Construir contenido enriquecido
                content = f"Título: {doc.get('titulo', '')}\n"
                
                # Agregar sección si existe
                if 'seccion' in doc:
                    content += f"Sección: {doc.get('seccion')}\n"
                
                content += f"Contenido: {doc.get('contenido', '')}"

                # Metadata plana para ChromaDB
                metadata = {
                    "source": "knowledge_json",
                    "id": doc.get("id", ""),
                    "type": doc.get("tipo", "unknown"),
                    "section": doc.get("seccion", "general"),
                    "tags": ", ".join(doc.get("tags", []))  # Chroma no soporta listas en metadata
                }
                
                documents.append(Document(page_content=content, metadata=metadata))

            if documents:
                # Opcional: Limpiar colección anterior antes de re-ingestar para evitar duplicados masivos
                # self.vector_store.delete_collection() -> Cuidado en prod
                # Por ahora solo añadimos (mejorar lógica de actualización en futuro)
                
                logger.info(f"Ingestando {len(documents)} vectores a ChromaDB...")
                self.vector_store.add_documents(documents)
                logger.info("Ingesta completada.")
            else:
                logger.warning("No se generaron documentos para ingestar.")

        except Exception as e:
            logger.error(f"Error ingestando conocimiento: {e}")

    def search(self, query: str, k: int = 3) -> List[Document]:
        """Busca documentos relevantes semánticamente."""
        if not self.vector_store:
            logger.warning("Vector store no inicializado.")
            return []
        
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return []

# Instancia global
rag_service = RAGService()
