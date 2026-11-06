<?php
/**
 * Uninstall Inova CMS Sync.
 *
 * Removes plugin options and custom tables.
 * Does NOT delete imported posts.
 *
 * @package Insight_CMS_Sync
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit;
}

global $wpdb;

$prefix = $wpdb->prefix . 'ics_';

$wpdb->query( "DROP TABLE IF EXISTS {$prefix}mapping" );
$wpdb->query( "DROP TABLE IF EXISTS {$prefix}log" );

delete_option( 'ics_settings' );
delete_option( 'ics_db_version' );
delete_option( 'ics_sync_cursor' );
delete_transient( 'ics_agents_cache' );
