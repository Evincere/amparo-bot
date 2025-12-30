from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List

class UIComponent(BaseModel):
    """Componente de interfaz gráfica."""
    type: Literal["text", "card", "alert", "chart", "action_button"]
    title: Optional[str] = Field(None, description="Título del componente")
    content: str = Field(..., description="Contenido textual o descripción")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos estructurados adicionales (ej: id_expediente, url)")
    alert_level: Optional[Literal["info", "warning", "success", "error"]] = Field("info", description="Solo para type='alert'")

class AgentResponse(BaseModel):
    """Respuesta estructurada del agente."""
    components: List[UIComponent]
