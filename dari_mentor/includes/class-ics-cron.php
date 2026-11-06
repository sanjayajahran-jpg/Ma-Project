<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Cron {

	private $importer;
	private $settings;
	private $logger;

	public function __construct( ICS_Importer $importer, ICS_Settings $settings, ICS_Logger $logger ) {
		$this->importer = $importer;
		$this->settings  = $settings;
		$this->logger   = $logger;
	}

	public function register_intervals( $schedules ) {
		$schedules['ics_15min'] = array(
			'interval' => 15 * MINUTE_IN_SECONDS,
			'display'  => __( 'Setiap 15 Menit', 'inova-cms-sync' ),
		);
		$schedules['ics_30min'] = array(
			'interval' => 30 * MINUTE_IN_SECONDS,
			'display'  => __( 'Setiap 30 Menit', 'inova-cms-sync' ),
		);
		$schedules['ics_6hour'] = array(
			'interval' => 6 * HOUR_IN_SECONDS,
			'display'  => __( 'Setiap 6 Jam', 'inova-cms-sync' ),
		);
		$schedules['ics_12hour'] = array(
			'interval' => 12 * HOUR_IN_SECONDS,
			'display'  => __( 'Setiap 12 Jam', 'inova-cms-sync' ),
		);
		return $schedules;
	}

	public function get_recurrence( $interval_key ) {
		$map = array(
			'15min'  => 'ics_15min',
			'30min'  => 'ics_30min',
			'1hour'  => 'hourly',
			'6hour'  => 'ics_6hour',
			'12hour' => 'ics_12hour',
			'daily'  => 'daily',
		);
		return isset( $map[ $interval_key ] ) ? $map[ $interval_key ] : 'ics_30min';
	}

	public function schedule() {
		if ( ! $this->settings->get( 'sync_enabled' ) ) {
			$this->unschedule();
			return;
		}

		$interval = $this->settings->get( 'interval', '30min' );
		$recurrence = $this->get_recurrence( $interval );

		if ( ! wp_next_scheduled( 'ics_cron_sync' ) ) {
			wp_schedule_event( time(), $recurrence, 'ics_cron_sync' );
		}
	}

	public function unschedule() {
		$timestamp = wp_next_scheduled( 'ics_cron_sync' );
		if ( $timestamp ) {
			wp_unschedule_event( $timestamp, 'ics_cron_sync' );
		}
	}

	public function run_sync() {
		$lock = get_transient( 'ics_sync_lock' );
		if ( $lock ) {
			return;
		}
		set_transient( 'ics_sync_lock', 1, 5 * MINUTE_IN_SECONDS );

		$result = $this->importer->sync_batch();
		delete_transient( 'ics_sync_lock' );

		if ( is_wp_error( $result ) ) {
			$this->logger->log( '', 0, 'sync', 'failed', $result->get_error_message() );
		}
	}
}
