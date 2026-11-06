<?php
/**
 * Plugin Name:       Inova CMS Sync
 * Plugin URI:        https://plugins.inova.id
 * Description:       Sinkronisasi artikel dari Inova CMS ke WordPress + AI Writer langsung dari editor post.
 * Version:           1.2.3
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Inova
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       inova-cms-sync
 * Domain Path:       /languages
 *
 * @package Insight_CMS_Sync
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'ICS_VERSION', '1.2.3' );
define( 'ICS_PLUGIN_FILE', __FILE__ );
define( 'ICS_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'ICS_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'ICS_PLUGIN_BASENAME', plugin_basename( __FILE__ ) );

require_once ICS_PLUGIN_DIR . 'includes/class-ics-plugin.php';

register_activation_hook( __FILE__, array( 'ICS_Activator', 'activate' ) );
register_deactivation_hook( __FILE__, array( 'ICS_Activator', 'deactivate' ) );

function ics() {
	return ICS_Plugin::instance();
}

ics();
