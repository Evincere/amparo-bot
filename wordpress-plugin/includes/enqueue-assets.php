<?php
/**
 * Enqueue de assets (CSS y JS) del widget
 */

// Si se accede directamente, salir
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Cargar assets del frontend
 */
function dmchat_enqueue_assets() {
    // Verificar si el widget está habilitado
    if (get_option('dmchat_enabled') !== '1') {
        return;
    }
    
    // No cargar en páginas de administración
    if (is_admin()) {
        return;
    }
    
    // CSS del widget
    wp_enqueue_style(
        'dmchat-widget-css',
        DMCHAT_PLUGIN_URL . 'assets/css/chat-widget.css',
        array(),
        DMCHAT_VERSION,
        'all'
    );
    
    // JavaScript del widget
    wp_enqueue_script(
        'dmchat-widget-js',
        DMCHAT_PLUGIN_URL . 'assets/js/chat-widget.js',
        array(),
        DMCHAT_VERSION,
        true // Cargar en footer
    );
    
    // Pasar configuración PHP a JavaScript
    $config = array(
        'apiUrl' => esc_url(get_option('dmchat_backend_url', 'http://localhost:8000')),
        'welcomeMessage' => esc_html(get_option('dmchat_welcome_message', '¡Hola! Soy Amparo, ¿en qué puedo ayudarte?')),
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('dmchat_nonce')
    );
    
    wp_localize_script('dmchat-widget-js', 'dmChatConfig', $config);
}
add_action('wp_enqueue_scripts', 'dmchat_enqueue_assets');

/**
 * Enqueue de assets del admin
 */
function dmchat_enqueue_admin_assets($hook) {
    // Solo cargar en nuestra página de configuración
    if ($hook !== 'toplevel_page_dmchat-settings') {
        return;
    }
    
    // CSS personalizado del admin (si es necesario)
    wp_enqueue_style(
        'dmchat-admin-css',
        DMCHAT_PLUGIN_URL . 'assets/css/admin.css',
        array(),
        DMCHAT_VERSION
    );
}
add_action('admin_enqueue_scripts', 'dmchat_enqueue_admin_assets');
