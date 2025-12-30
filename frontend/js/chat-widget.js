/**
 * Widget de Chat - Defensa Pública de Mendoza
 * JavaScript con integración al backend FastAPI
 */

(function () {
    'use strict';

    // Configuración (será inyectada por WordPress)
    const config = window.dmChatConfig || {
        apiUrl: 'http://localhost:8001',
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
                <img src="assets/logos/icono.png" alt="Chat Icon" />
            </button>
            
            <!-- Contenedor del chat -->
            <div class="dm-chat-container" id="dmChatContainer">
                <!-- Header -->
                <div class="dm-chat-header">
                    <div class="dm-chat-header-info">
                        <div class="dm-chat-avatar">
                            <img src="assets/logos/icono.png" alt="Amparo Avatar" />
                        </div>
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
    function addMessage(text, type = 'bot', agentName = null, returnDiv = false) {
        const messagesContainer = document.getElementById('dmChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `dm-chat-message ${type}`;

        const avatarHTML = type === 'bot'
            ? `<img src="assets/logos/icono.png" alt="Bot" />`
            : 'U';

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
            <div class="dm-chat-message-avatar">${avatarHTML}</div>
            <div class="dm-chat-message-content">
                <div class="dm-chat-message-bubble">${text ? escapeHTML(text) : ''}</div>
                ${badgeHTML}
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();

        // Guardar en estado
        if (text) state.messages.push({ text, type, agentName });

        if (returnDiv) return messageDiv;
    }

    // Mostrar indicador de escritura
    function showTypingIndicator() {
        const messagesContainer = document.getElementById('dmChatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'dm-chat-message bot';
        typingDiv.id = 'dmTypingIndicator';
        typingDiv.innerHTML = `
            <div class="dm-chat-message-avatar">
                <img src="assets/logos/icono.png" alt="Bot" />
            </div>
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

    // Renderizar componentes UI
    function renderUIComponent(component) {
        const type = component.type;
        const content = component.content || '';
        const title = component.title || '';

        let html = '';

        if (type === 'card') {
            html = `
                <div class="dm-card">
                    ${title ? `<div class="dm-card-title">${escapeHTML(title)}</div>` : ''}
                    <div class="dm-card-content">${markdownToHTML(content)}</div>
                    ${component.data ? `<div class="dm-card-data"><pre>${JSON.stringify(component.data, null, 2)}</pre></div>` : ''}
                </div>
            `;
        } else if (type === 'alert') {
            const level = component.alert_level || 'info';
            html = `
                <div class="dm-alert dm-alert-${level}">
                    ${title ? `<strong>${escapeHTML(title)}</strong><br>` : ''}
                    ${markdownToHTML(content)}
                </div>
            `;
        } else if (type === 'action_button') {
            const btnId = 'btn_' + Math.random().toString(36).substr(2, 9);
            // Store data if needed, or just use content/title as payload
            const payload = component.data && component.data.payload ? component.data.payload : (title || content);

            html = `
                <button 
                    class="dm-action-button" 
                    onclick="window.dmChatWidget.sendAction('${escapeHTML(payload)}')"
                >
                    <div class="dm-btn-content">
                        ${title ? `<div class="dm-btn-title">${escapeHTML(title)}</div>` : ''}
                        ${content ? `<div class="dm-btn-desc">${escapeHTML(content)}</div>` : ''}
                    </div>
                </button>
            `;
        } else {
            // Text default
            html = markdownToHTML(content);
        }

        return html;
    }

    // Exponer función para enviar acciones desde botones
    window.dmChatWidget = {
        sendAction: function (text) {
            const input = document.getElementById('dmChatInput');
            if (input) {
                input.value = text;
                // Disparar evento de envío
                const sendBtn = document.getElementById('dmChatSend');
                if (sendBtn) sendBtn.click();
            }
        }
    };

    // Convertir simple markdown a HTML (negritas y saltos)
    function markdownToHTML(text) {
        if (!text) return '';
        let html = escapeHTML(text);
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
        html = html.replace(/\n/g, '<br>'); // Newlines
        return html;
    }

    // Enviar mensaje al backend con Streaming
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
            const response = await fetch(`${config.apiUrl}/api/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: state.sessionId
                })
            });

            if (!response.ok) throw new Error('Error en conexión');

            // Leer stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            // Ocultar typing al empezar a recibir datos
            hideTypingIndicator();

            let assistantMessageDiv = null;
            let currentContent = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const eventData = JSON.parse(line.slice(6));

                            if (eventData.type === 'metadata') {
                                if (eventData.session_id) state.sessionId = eventData.session_id;
                            }
                            else if (eventData.type === 'content') {
                                const content = eventData.content;
                                // console.log('Received content type:', typeof content, content); // DEBUG

                                // Si el contenido ya viene como objeto estructurado (JSON ya parseado)
                                if (typeof content === 'object' && content !== null) {
                                    // Es una respuesta estructurada completa
                                    if (!assistantMessageDiv) {
                                        assistantMessageDiv = addMessage('', 'bot', null, true);
                                    }
                                    const bubble = assistantMessageDiv.querySelector('.dm-chat-message-bubble');
                                    bubble.innerHTML = ''; // Reset

                                    // Renderizar content si existe (resumen)
                                    if (content.content) {
                                        const contentDiv = document.createElement('div');
                                        contentDiv.innerHTML = markdownToHTML(content.content);
                                        bubble.appendChild(contentDiv);
                                    }

                                    // Renderizar componentes
                                    if (content.components && Array.isArray(content.components)) {
                                        content.components.forEach(comp => {
                                            const compHTML = renderUIComponent(comp);
                                            const div = document.createElement('div');
                                            div.innerHTML = compHTML;
                                            bubble.appendChild(div);
                                        });
                                    }

                                    scrollToBottom();
                                    return; // Ya manejamos este chunk
                                }

                                // Si es la primera vez, crear burbuja del bot
                                if (!assistantMessageDiv) {
                                    assistantMessageDiv = addMessage('', 'bot', null, true); // true = return div
                                }

                                // Texto plano o progresivo
                                currentContent += content;

                                // Intentar detectar JSON estructurado en el contenido acumulado
                                // Solo si parece empezar con una llave JSON
                                if (currentContent.trim().startsWith('{')) {
                                    try {
                                        // Intentamos parsear el contenido acumulado hasta ahora
                                        // Nota: Esto fallará hasta que el JSON esté completo, lo cual es esperado durante el streaming
                                        // Una vez completo, renderizamos los componentes
                                        const parsed = JSON.parse(currentContent);
                                        if (parsed.components) {
                                            // Es una respuesta estructurada completa
                                            // Limpiamos lo que hubiera y renderizamos componentes
                                            const bubble = assistantMessageDiv.querySelector('.dm-chat-message-bubble');
                                            bubble.innerHTML = ''; // Reset

                                            // Renderizar content si existe (resumen)
                                            if (parsed.content) {
                                                const contentDiv = document.createElement('div');
                                                contentDiv.innerHTML = markdownToHTML(parsed.content);
                                                bubble.appendChild(contentDiv);
                                            }

                                            parsed.components.forEach(comp => {
                                                const compHTML = renderUIComponent(comp);
                                                const div = document.createElement('div');
                                                div.innerHTML = compHTML;
                                                bubble.appendChild(div);
                                            });
                                            scrollToBottom();
                                            return; // Ya manejamos este chunk como parte del JSON final
                                        }
                                    } catch (e) {
                                        // JSON incompleto, seguimos acumulando
                                    }
                                }

                                const bubble = assistantMessageDiv.querySelector('.dm-chat-message-bubble');
                                bubble.innerHTML = markdownToHTML(currentContent);


                                scrollToBottom();
                            }
                        } catch (e) {
                            console.error('Error parsing SSE:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            hideTypingIndicator();
            addMessage(
                'Disculpa, estoy teniendo problemas de conexión.',
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
