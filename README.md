# Bot de Consulta - Defensa Pública de Mendoza

Sistema inteligente de consultas con agentes especializados por fuero, integrado en WordPress mediante widget flotante.

## 🎯 Características

- **6 Agentes Especializados**: General, Civil, Familia, Penal, Penal Juvenil y NNA/PCR
- **Router Inteligente**: Clasificación automática de consultas basada en keywords
- **Diseño Premium**: Widget con diseño granate institucional (#800000)
- **Integración WordPress**: Plugin custom fácil de instalar
- **Powered by Ollama Cloud**: Utiliza modelos de lenguaje de última generación

## 📁 Estructura del Proyecto

```
prime-perigee/
├── backend/                    # Backend FastAPI + LangChain
│   ├── app/
│   │   ├── agents/            # Agentes especializados
│   │   │   ├── base_agent.py
│   │   │   ├── agent_router.py
│   │   │   ├── general_agent.py
│   │   │   ├── civil_agent.py
│   │   │   ├── familia_agent.py
│   │   │   ├── penal_agent.py
│   │   │   ├── penal_juvenil_agent.py
│   │   │   └── nna_pcr_agent.py
│   │   ├── services/
│   │   │   ├── knowledge_base.py
│   │   │   └── chat_service.py
│   │   ├── config.py
│   │   └── main.py            # Aplicación FastAPI
│   ├── data/
│   │   └── knowledge_example.json
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
├── frontend/                   # Widget HTML/CSS/JS
│   ├── css/
│   │   └── chat-widget.css
│   └── js/
│       └── chat-widget.js
│
└── wordpress-plugin/           # Plugin WordPress
    ├── assets/
    │   ├── css/
    │   │   └── chat-widget.css
    │   └── js/
    │       └── chat-widget.js
    ├── includes/
    │   ├── enqueue-assets.php
    │   └── admin-settings.php
    └── defensamendoza-chatbot.php
```

## 🚀 Instalación

### 1. Backend (FastAPI + Ollama Cloud)

#### Requisitos
- Python 3.9 o superior
- Cuenta en [Ollama Cloud](https://ollama.com) con API key

#### Pasos

```bash
# 1. Navegar al directorio backend
cd backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
copy .env.example .env
# Editar .env y configurar:
# - OLLAMA_API_KEY=tu_api_key_aqui
# - OLLAMA_MODEL=gpt-oss:120b
# - CORS_ORIGINS=https://defensamendoza.gob.ar

# 6. Preparar base de conocimiento
# Copiar knowledge_example.json a knowledge.json y completar con datos reales
copy data\knowledge_example.json data\knowledge.json

# 7. Ejecutar servidor
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000`

#### Endpoints Disponibles

- `GET /` - Información del API
- `GET /api/health` - Health check
- `GET /api/fueros` - Lista de fueros disponibles
- `POST /api/chat` - Enviar mensaje (formato JSON)
- `POST /api/chat/stream` - Chat con streaming (SSE)
- `DELETE /api/session/{session_id}` - Limpiar sesión

### 2. Plugin WordPress

#### Instalación Manual

```bash
# 1. Comprimir carpeta wordpress-plugin
# Renombrar a: defensamendoza-chatbot.zip

# 2. En WordPress Admin:
# - Ir a Plugins → Add New → Upload Plugin
# - Seleccionar defensamendoza-chatbot.zip
# - Click en "Install Now"
# - Activar plugin

# 3. Configurar:
# - Ir a "Bot Consulta" en el menú lateral
# - Configurar URL del backend
# - Personalizar mensaje de bienvenida
# - Probar conexión
# - Guardar cambios
```

#### Instalación vía FTP

```bash
# 1. Subir carpeta wordpress-plugin a:
/wp-content/plugins/defensamendoza-chatbot/

# 2. Activar desde panel de WordPress
```

## ⚙️ Configuración

### Backend

Editar `backend/.env`:

```env
# Ollama Cloud
OLLAMA_API_KEY=sk_ollama_xxxxxxxxxxxxx
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_HOST=https://ollama.com

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS (WordPress domain)
CORS_ORIGINS=https://defensamendoza.gob.ar,https://www.defensamendoza.gob.ar

# Knowledge Base
KNOWLEDGE_FILE=data/knowledge.json
```

### WordPress Plugin

En WordPress Admin → Bot Consulta:

- **URL del Backend**: `https://api-bot.defensamendoza.gob.ar` (o tu URL)
- **Activar Widget**: ✅ Marcado
- **Mensaje de Bienvenida**: Personalizar según preferencia

## 📊 Base de Conocimiento (JSON)

El archivo `backend/data/knowledge.json` contiene la información que el bot utilizará para responder.

**Estructura básica:**

```json
{
  "metadata": { "version": "1.0", ... },
  "general": {
    "institucional": {...},
    "contacto": {...},
    "horarios_generales": {...},
    "preguntas_frecuentes": [...]
  },
  "fueros": {
    "civil": {...},
    "familia": {...},
    "penal": {...},
    "penal_juvenil": {...},
    "nna_pcr": {...}
  }
}
```

Ver `json_structure_example.md` para estructura completa con ejemplos.

## 🎨 Personalización

### Colores del Widget

Editar `wordpress-plugin/assets/css/chat-widget.css`:

```css
:root {
  --color-primary: #800000;  /* Color institucional */
  --color-primary-dark: #5c0000;
  --color-primary-light: #a31a1a;
}
```

### Prompts de Agentes

Editar los archivos en `backend/app/agents/*_agent.py`, método `get_system_prompt()`.

## 🧪 Pruebas

### Test del Backend

```bash
# Health check
curl http://localhost:8000/api/health

# Lista de fueros
curl http://localhost:8000/api/fueros

# Enviar mensaje de prueba
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, necesito ayuda"}'
```

### Test del Widget

1. Abrir sitio de WordPress
2. Buscar botón flotante granate en esquina inferior derecha
3. Click para abrir chat
4. Enviar mensaje de prueba
5. Verificar respuesta del bot

## 📝 Mantenimiento

### Actualizar Base de Conocimiento

Dos opciones:

**Opción 1: Sin reiniciar (requiere admin API key)**
```bash
curl -X POST http://localhost:8000/api/admin/reload?api_key=tu_admin_key
```

**Opción 2: Editar JSON y reiniciar backend**
```bash
# 1. Editar backend/data/knowledge.json
# 2. Reiniciar servidor backend
```

### Logs del Backend

Los logs se imprimen en consola. Para producción, configurar logging a archivo.

## 🔒 Seguridad

- ✅ CORS configurado solo para dominios autorizados
- ✅ Rate limiting en endpoints (10 requests/minuto)
- ✅ Sanitización de inputs
- ✅ Validación con Pydantic
- ✅ Longitud máxima de mensajes: 500 caracteres

## 📈 Mejoras Futuras

- [ ] Implementar Redis para sesiones persistentes
- [ ] Agregar analytics de uso
- [ ] Dashboard de estadísticas
- [ ] Soporte multiidioma
- [ ] Versión móvil nativa
- [ ] Integración con WhatsApp Business

## 🆘 Troubleshooting

### El widget no aparece

✅ Verificar que el plugin está activado  
✅ Verificar que "Activar Widget" está marcado en configuración  
✅ Revisar consola del navegador por errores JavaScript  

### Error de CORS

✅ Verificar `CORS_ORIGINS` en backend `.env`  
✅ Asegurar que URL en WordPress coincide con la configurada  
✅ Verificar headers en DevTools → Network  

### Backend no responde

✅ Verificar que el servidor está corriendo  
✅ Test de health: `curl http://localhost:8000/api/health`  
✅ Revisar logs del servidor  
✅ Verificar API key de Ollama Cloud  

### Respuestas incorrectas

✅ Revisar/actualizar `knowledge.json`  
✅ Verificar keywords de agentes  
✅ Ajustar prompts de sistema  

## 📧 Soporte

- **Email**: soporte@defensamendoza.gob.ar
- **Documentación**: Ver carpeta `docs/`
- **Issues**: Contactar al equipo de desarrollo

## 📄 Licencia

Desarrollado para el Ministerio de la Defensa Pública de Mendoza.

---

**Versión**: 1.0.0  
**Última actualización**: 27 de Diciembre de 2025
