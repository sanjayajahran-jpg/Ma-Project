<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Activator {

	public static function activate() {
		self::create_tables();
		self::register_cron();
		update_option( 'ics_db_version', '1.0.0' );
	}

	public static function deactivate() {
		wp_clear_scheduled_hook( 'ics_cron_sync' );
	}

	private static function create_tables() {
		global $wpdb;
		require_once ABSPATH . 'wp-admin/includes/upgrade.php';

		$charset_collate = $wpdb->get_charset_collate();
		$prefix = $wpdb->prefix . 'ics_';

		$sql_mapping = "CREATE TABLE {$prefix}mapping (
			id                  bigint(20) NOT NULL AUTO_INCREMENT,
			remote_article_id   varchar(100) NOT NULL,
			wp_post_id          bigint(20) NOT NULL DEFAULT 0,
			remote_updated_at   varchar(50) DEFAULT NULL,
			synced_at           datetime DEFAULT NULL,
			origin              varchar(10) NOT NULL DEFAULT 'sync',
			PRIMARY KEY  (id),
			UNIQUE KEY remote_article_id (remote_article_id)
		) {$charset_collate};";

		$sql_log = "CREATE TABLE {$prefix}log (
			id                  bigint(20) NOT NULL AUTO_INCREMENT,
			remote_article_id   varchar(100) NOT NULL DEFAULT '',
			wp_post_id          bigint(20) NOT NULL DEFAULT 0,
			type                varchar(10) NOT NULL DEFAULT 'sync',
			status              varchar(10) NOT NULL DEFAULT 'info',
			message             text,
			created_at          datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
			PRIMARY KEY  (id),
			KEY type (type),
			KEY created_at (created_at)
		) {$charset_collate};";

		dbDelta( $sql_mapping );
		dbDelta( $sql_log );
	}

	private static function register_cron() {
		add_filter( 'cron_schedules', array( __CLASS__, 'add_intervals' ) );
	}

	public static function add_intervals( $schedules ) {
		$schedules['ics_15min']  = array( 'interval' => 900,   'display' => 'ICS 15 Min' );
		$schedules['ics_30min']  = array( 'interval' => 1800,  'display' => 'ICS 30 Min' );
		$schedules['ics_6hour']  = array( 'interval' => 21600, 'display' => 'ICS 6 Jam' );
		$schedules['ics_12hour'] = array( 'interval' => 43200, 'display' => 'ICS 12 Jam' );
		return $schedules;
	}
}
