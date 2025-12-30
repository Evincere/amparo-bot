<?php
/**
 * Panel de configuración en el administrador de WordPress
 */

// Si se accede directamente, salir
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Agregar menú al admin
 */
function dmchat_add_admin_menu() {
    add_menu_page(
        'Bot de Consulta - Configuración',  // Page title
        'Bot Consulta',                      // Menu title
        'manage_options',                    // Capability
        'dmchat-settings',                   // Menu slug
        'dmchat_settings_page',              // Callback function
        'dashicons-format-chat',             // Icon
        80                                   // Position
    );
}
add_action('admin_menu', 'dmchat_add_admin_menu');

/**
 * Página de configuración
 */
function dmchat_settings_page() {
    ?>
    <div class="wrap">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
        
        <?php settings_errors('dmchat_messages'); ?>
        
        <form method="post" action="options.php">
            <?php
            settings_fields('dmchat_settings');
            do_settings_sections('dmchat-settings');
            submit_button('Guardar Configuración');
            ?>
        </form>
        
        <hr>
        
        <div class="dmchat-info-box" style="background: #f9f9f9; padding: 20px; border-left: 4px solid #800000; margin-top: 20px;">
            <h3>ℹ️ Información del Plugin</h3>
            <p><strong>Versión:</strong> <?php echo DMCHAT_VERSION; ?></p>
            <p><strong>Documentación:</strong> <a href="https://defensamendoza.gob.ar/docs/chatbot" target="_blank">Ver documentación completa</a></p>
            <p><strong>Soporte:</strong> <a href="mailto:soporte@defensamendoza.gob.ar">soporte@defensamendoza.gob.ar</a></p>
        </div>
        
        <div class="dmchat-test-box" style="background: #fff; padding: 20px; border: 1px solid #ddd; margin-top: 20px;">
            <h3>🧪 Probar Conexión al Backend</h3>
            <button type="button" id="dmchat-test-connection" class="button button-secondary">Probar Conexión</button>
            <div id="dmchat-test-result" style="margin-top: 10px;"></div>
        </div>
    </div>
    
    <script>
    document.getElementById('dmchat-test-connection').addEventListener('click', async function() {
        const resultDiv = document.getElementById('dmchat-test-result');
        const backendUrl = document.querySelector('input[name="dmchat_backend_url"]').value;
        
        resultDiv.innerHTML = '<p>⏳ Probando conexión...</p>';
        
        try {
            const response = await fetch(backendUrl + '/api/health');
            const data = await response.json();
            
            if (response.ok && data.status === 'healthy') {
                resultDiv.innerHTML = '<p style="color: green;">✅ Conexión exitosa! Backend funcionando correctamente.</p>';
            } else {
                resultDiv.innerHTML = '<p style="color: orange;">⚠️ Backend respondió pero con estado: ' + data.status + '</p>';
            }
        } catch (error) {
            resultDiv.innerHTML = '<p style="color: red;">❌ Error de conexión: ' + error.message + '</p>';
        }
    });
    </script>
    <?php
}

/**
 * Registrar configuraciones
 */
function dmchat_register_settings() {
    // Registrar opciones
    register_setting('dmchat_settings', 'dmchat_backend_url', array(
        'type' => 'string',
        'sanitize_callback' => 'esc_url_raw',
        'default' => 'http://localhost:8000'
    ));
    
    register_setting('dmchat_settings', 'dmchat_enabled', array(
        'type' => 'string',
        'sanitize_callback' => 'sanitize_text_field',
        'default' => '1'
    ));
    
    register_setting('dmchat_settings', 'dmchat_welcome_message', array(
        'type' => 'string',
        'sanitize_callback' => 'sanitize_textarea_field',
        'default' => '¡Hola! Soy Amparo, ¿en qué puedo ayudarte?'
    ));
    
    // Sección principal
    add_settings_section(
        'dmchat_main_section',
        'Configuración General',
        'dmchat_main_section_callback',
        'dmchat-settings'
    );
    
    // Campo: URL del Backend
    add_settings_field(
        'dmchat_backend_url',
        'URL del Backend',
        'dmchat_backend_url_callback',
        'dmchat-settings',
        'dmchat_main_section'
    );
    
    // Campo: Activar Widget
    add_settings_field(
        'dmchat_enabled',
        'Activar Widget',
        'dmchat_enabled_callback',
        'dmchat-settings',
        'dmchat_main_section'
    );
    
    // Campo: Mensaje de Bienvenida
    add_settings_field(
        'dmchat_welcome_message',
        'Mensaje de Bienvenida',
        'dmchat_welcome_message_callback',
        'dmchat-settings',
        'dmchat_main_section'
    );
}
add_action('admin_init', 'dmchat_register_settings');

/**
 * Callbacks de secciones y campos
 */
function dmchat_main_section_callback() {
    echo '<p>Configura los parámetros del bot de consulta.</p>';
}

function dmchat_backend_url_callback() {
    $value = get_option('dmchat_backend_url', 'http://localhost:8000');
    ?>
    <input type="url" 
           name="dmchat_backend_url" 
           value="<?php echo esc_attr($value); ?>" 
           class="regular-text"
           placeholder="https://api-bot.defensamendoza.gob.ar"
    />
    <p class="description">
        URL completa del servidor backend FastAPI (ejemplo: https://api-bot.defensamendoza.gob.ar)<br>
        <strong>Importante:</strong> Debe incluir <code>https://</code> o <code>http://</code>
    </p>
    <?php
}

function dmchat_enabled_callback() {
    $value = get_option('dmchat_enabled', '1');
    ?>
    <label>
        <input type="checkbox" 
               name="dmchat_enabled" 
               value="1" 
               <?php checked('1', $value); ?>
        />
        Mostrar el widget en el sitio web
    </label>
    <p class="description">
        Desmarca esta opción para ocultar temporalmente el widget sin desactivar el plugin.
    </p>
    <?php
}

function dmchat_welcome_message_callback() {
    $value = get_option('dmchat_welcome_message', '¡Hola! Soy Amparo, ¿en qué puedo ayudarte?');
    ?>
    <textarea name="dmchat_welcome_message" 
              rows="3" 
              class="large-text"
              placeholder="Escribe el mensaje de bienvenida..."
    ><?php echo esc_textarea($value); ?></textarea>
    <p class="description">
        Mensaje que se muestra al abrir el chat por primera vez.
    </p>
    <?php
}
