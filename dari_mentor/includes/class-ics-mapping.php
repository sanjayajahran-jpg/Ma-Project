<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Mapping {

	public function get_wp_post_id( $remote_article_id ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_mapping';
		return (int) $wpdb->get_var( $wpdb->prepare(
			"SELECT wp_post_id FROM {$table} WHERE remote_article_id = %s",
			$remote_article_id
		) );
	}

	public function get_remote_updated_at( $remote_article_id ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_mapping';
		return $wpdb->get_var( $wpdb->prepare(
			"SELECT remote_updated_at FROM {$table} WHERE remote_article_id = %s",
			$remote_article_id
		) );
	}

	public function save_mapping( $remote_article_id, $wp_post_id, $remote_updated_at, $origin = 'sync' ) {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_mapping';

		$existing = $this->get_wp_post_id( $remote_article_id );

		if ( $existing ) {
			$wpdb->update(
				$table,
				array(
					'wp_post_id'         => $wp_post_id,
					'remote_updated_at'  => $remote_updated_at,
					'synced_at'          => current_time( 'mysql' ),
				),
				array( 'remote_article_id' => $remote_article_id ),
				array( '%d', '%s', '%s' ),
				array( '%s' )
			);
		} else {
			$wpdb->insert(
				$table,
				array(
					'remote_article_id'  => $remote_article_id,
					'wp_post_id'         => $wp_post_id,
					'remote_updated_at'  => $remote_updated_at,
					'synced_at'          => current_time( 'mysql' ),
					'origin'             => $origin,
				),
				array( '%s', '%d', '%s', '%s', '%s' )
			);
		}
	}

	public function get_stats() {
		global $wpdb;
		$table = $wpdb->prefix . 'ics_mapping';
		$total = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" );
		$sync  = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table} WHERE origin = 'sync'" );
		$ai    = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$table} WHERE origin = 'ai'" );
		return compact( 'total', 'sync', 'ai' );
	}
}
