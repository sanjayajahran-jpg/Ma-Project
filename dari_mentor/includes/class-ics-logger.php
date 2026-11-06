<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Logger {

	public function log( $remote_article_id, $wp_post_id, $type, $status, $message = '' ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_log';
		$wpdb->insert(
			$table,
			array(
				'remote_article_id' => $remote_article_id ?: '',
				'wp_post_id'        => $wp_post_id ?: 0,
				'type'              => $type,
				'status'            => $status,
				'message'           => $message,
			),
			array( '%s', '%d', '%s', '%s', '%s' )
		);
	}

	public function get_logs( $limit = 50, $offset = 0, $type_filter = '' ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_log';
		$sql = "SELECT * FROM {$table}";
		$args = array();

		if ( $type_filter ) {
			$sql .= " WHERE type = %s";
			$args[] = $type_filter;
		}

		$sql   .= " ORDER BY created_at DESC LIMIT %d OFFSET %d";
		$args[] = $limit;
		$args[] = $offset;

		return $wpdb->get_results( $wpdb->prepare( $sql, $args ) );
	}

	public function count_logs( $type_filter = '' ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_log';
		if ( $type_filter ) {
			return (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$table} WHERE type = %s", $type_filter ) );
		}
		return (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" );
	}

	public function prune( $days = 30 ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_log';
		$wpdb->query( $wpdb->prepare( "DELETE FROM {$table} WHERE created_at < DATE_SUB(NOW(), INTERVAL %d DAY)", $days ) );
	}

	public function clear_all() {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_log';
		$wpdb->query( "TRUNCATE TABLE {$table}" );
	}
}
