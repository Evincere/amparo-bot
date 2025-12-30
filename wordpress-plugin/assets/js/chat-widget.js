/**
 * Widget de Chat - Defensa Pública de Mendoza
 * JavaScript con integración al backend FastAPI
 */

(function () {
    'use strict';

    // Configuración (será inyectada por WordPress)
    const config = window.dmChatConfig || {
        apiUrl: 'http://localhost:8000',
        welcomeMessage: '¡Hola! Soy Amparo, ¿en qué puedo ayudarte?'
    };

    // Estado del widget
    const state = {
        isOpen: false,
        isLoading: false,
        sessionId: null,
        messages: []
    };

    // Generar session ID único
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Crear HTML del widget
    function createWidgetHTML() {
        return `
            <!-- Botón flotante -->
            <button class="dm-chat-button" id="dmChatToggle" aria-label="Abrir chat">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    <path d="M7 9h2v2H7zm4 0h2v2h-2zm4 0h2v2h-2z"/>
                </svg>
            </button>
            
            <!-- Contenedor del chat -->
            <div class="dm-chat-container" id="dmChatContainer">
                <!-- Header -->
                <div class="dm-chat-header">
                    <div class="dm-chat-header-info">
                        <div class="dm-chat-avatar">A</div>
                        <div class="dm-chat-title">
                            <h3>Amparo</h3>
                            <p>Defensa Pública de Mendoza</p>
                        </div>
                    </div>
                    <button class="dm-chat-close" id="dmChatClose" aria-label="Cerrar chat">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Área de mensajes -->
                <div class="dm-chat-messages" id="dmChatMessages">
                    <div class="dm-welcome-message">
                        <h4>¡Bienvenido!</h4>
                        <p>${config.welcomeMessage}</p>
                    </div>
                </div>
                
                <!-- Input de mensajes -->
                <div class="dm-chat-input-container">
                    <input 
                        type="text" 
                        class="dm-chat-input" 
                        id="dmChatInput" 
                        placeholder="Escribe tu consulta..."
                        maxlength="500"
                    />
                    <button class="dm-chat-send-button" id="dmChatSend" aria-label="Enviar mensaje">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    // Añadir mensaje al chat
    function addMessage(text, type = 'bot', agentName = null) {
        const messagesContainer = document.getElementById('dmChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `dm-chat-message ${type}`;

        const avatar = type === 'bot' ? 'A' : 'U';

        let badgeHTML = '';
        if (type === 'bot' && agentName && agentName !== 'general') {
            const agentLabels = {
                'civil': 'Civil',
                'familia': 'Familia',
                'penal': 'Penal',
                'penal_juvenil': 'Penal Juvenil',
                'nna_pcr': 'NNA/PCR'
            };
            const label = agentLabels[agentName] || agentName;
            badgeHTML = `<div class="dm-agent-badge">${label}</div>`;
        }

        messageDiv.innerHTML = `
            <div class="dm-chat-message-avatar">${avatar}</div>
            <div class="dm-chat-message-content">
                <div class="dm-chat-message-bubble">${escapeHTML(text)}</div>
                ${badgeHTML}
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();

        // Guardar en estado
        state.messages.push({ text, type, agentName });
    }

    // Mostrar indicador de escritura
    function showTypingIndicator() {
        const messagesContainer = document.getElementById('dmChatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'dm-chat-message bot';
        typingDiv.id = 'dmTypingIndicator';
        typingDiv.innerHTML = `
            <div class="dm-chat-message-avatar">A</div>
            <div class="dm-typing-indicator">
                <div class="dm-typing-dot"></div>
                <div class="dm-typing-dot"></div>
                <div class="dm-typing-dot"></div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        scrollToBottom();
    }

    // Ocultar indicador de escritura
    function hideTypingIndicator() {
        const indicator = document.getElementById('dmTypingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Scroll al final
    function scrollToBottom() {
        const messagesContainer = document.getElementById('dmChatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Escapar HTML para prevenir XSS
    function escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    // Enviar mensaje al backend
    async function sendMessage(message) {
        if (!message.trim()) return;

        // Añadir mensaje del usuario
        addMessage(message, 'user');

        // Limpiar input
        const input = document.getElementById('dmChatInput');
        input.value = '';
        input.disabled = true;

        // Mostrar indicador de escritura
        showTypingIndicator();
        state.isLoading = true;

        try {
            // Llamada a API
            const response = await fetch(`${config.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: state.sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();

            // Actualizar session ID si es nueva
            if (data.session_id) {
                state.sessionId = data.session_id;
            }

            // Ocultar indicador y mostrar respuesta
            hideTypingIndicator();
            addMessage(data.response, 'bot', data.agent);

        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            hideTypingIndicator();
            addMessage(
                'Disculpa, estoy teniendo problemas de conexión. Por favor, intenta nuevamente o contacta al 0800-555-JUSTICIA.',
                'bot'
            );
        } finally {
            state.isLoading = false;
            input.disabled = false;
            input.focus();
        }
    }

    // Toggle widget
    function toggleWidget() {
        state.isOpen = !state.isOpen;
        const container = document.getElementById('dmChatContainer');
        const button = document.getElementById('dmChatToggle');

        if (state.isOpen) {
            container.classList.add('open');
            button.style.display = 'none';
            document.getElementById('dmChatInput').focus();
        } else {
            container.classList.remove('open');
            button.style.display = 'flex';
        }
    }

    // Inicializar widget
    function init() {
        // Crear contenedor en el body
        const widgetContainer = document.createElement('div');
        widgetContainer.id = 'dmChatWidget';
        widgetContainer.innerHTML = createWidgetHTML();
        document.body.appendChild(widgetContainer);

        // Generar session ID
        state.sessionId = generateSessionId();

        // Event listeners
        document.getElementById('dmChatToggle').addEventListener('click', toggleWidget);
        document.getElementById('dmChatClose').addEventListener('click', toggleWidget);

        const sendButton = document.getElementById('dmChatSend');
        const input = document.getElementById('dmChatInput');

        sendButton.addEventListener('click', () => {
            const message = input.value;
            sendMessage(message);
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !state.isLoading) {
                const message = input.value;
                sendMessage(message);
            }
        });

        // Deshabilitar botón send cuando input está vacío
        input.addEventListener('input', () => {
            sendButton.disabled = !input.value.trim() || state.isLoading;
        });

        console.log('Widget de chat inicializado correctamente');
    }

    // Iniciar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
