<?php
/**
 * Plugin Name: Defensa Mendoza - Bot de Consulta
 * Plugin URI: https://defensamendoza.gob.ar
 * Description: Bot inteligente de consulta con agentes especializados por fuero
 * Version: 1.0.0
 * Author: Defensa Pública de Mendoza
 * Author URI: https://defensamendoza.gob.ar
 * Text Domain: defensamendoza-chatbot
 * License: GPL-2.0+
 */

// Si se accede directamente, salir
if (!defined('ABSPATH')) {
    exit;
}

// Definir constantes del plugin
define('DMCHAT_VERSION', '1.0.0');
define('DMCHAT_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('DMCHAT_PLUGIN_URL', plugin_dir_url(__FILE__));
define('DMCHAT_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * Cargar archivos del plugin
 */
require_once DMCHAT_PLUGIN_DIR . 'includes/enqueue-assets.php';
require_once DMCHAT_PLUGIN_DIR . 'includes/admin-settings.php';

/**
 * Activación del plugin
 */
function dmchat_activate() {
    // Opciones por defecto
    add_option('dmchat_enabled', '1');
    add_option('dmchat_backend_url', 'http://localhost:8000');
    add_option('dmchat_welcome_message', '¡Hola! Soy Amparo, ¿en qué puedo ayudarte?');
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'dmchat_activate');

/**
 * Desactivación del plugin
 */
function dmchat_deactivate() {
    flush_rewrite_rules();
}
register_deactivation_hook(__FILE__, 'dmchat_deactivate');

/**
 * Desinstalación del plugin
 */
function dmchat_uninstall() {
    // Eliminar opciones (opcional, comentar si quiere mantener configuración)
    // delete_option('dmchat_enabled');
    // delete_option('dmchat_backend_url');
    // delete_option('dmchat_welcome_message');
}
register_uninstall_hook(__FILE__, 'dmchat_uninstall');

/**
 * Link de configuración en la página de plugins
 */
function dmchat_settings_link($links) {
    $settings_link = '<a href="admin.php?page=dmchat-settings">Configuración</a>';
    array_unshift($links, $settings_link);
    return $links;
}
add_filter('plugin_action_links_' . DMCHAT_PLUGIN_BASENAME, 'dmchat_settings_link');
