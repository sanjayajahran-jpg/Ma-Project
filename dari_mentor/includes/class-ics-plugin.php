<?php
if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * Main plugin singleton.
 */
class ICS_Plugin {

	private static $instance = null;

	public $client;
	public $settings;
	public $importer;
	public $media;
	public $mapping;
	public $cron;
	public $logger;
	public $admin;
	public $editor;
	public $updater;

	public static function instance() {
		if ( null === self::$instance ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	private function __construct() {
		$this->load_dependencies();
		$this->init_hooks();
	}

	private function load_dependencies() {
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-logger.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-settings.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-mapping.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-client.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-media.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-importer.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-cron.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-activator.php';
		require_once ICS_PLUGIN_DIR . 'includes/class-ics-updater.php';

		if ( is_admin() ) {
			require_once ICS_PLUGIN_DIR . 'admin/class-ics-admin.php';
			require_once ICS_PLUGIN_DIR . 'admin/class-ics-editor.php';
		}
	}

	private function init_hooks() {
		$this->logger   = new ICS_Logger();
		$this->settings = new ICS_Settings();
		$this->mapping  = new ICS_Mapping();
		$this->client   = new ICS_Client( $this->settings );
		$this->media    = new ICS_Media( $this->client, $this->settings );
		$this->importer = new ICS_Importer( $this->client, $this->settings, $this->media, $this->mapping, $this->logger );
		$this->cron     = new ICS_Cron( $this->importer, $this->settings, $this->logger );

		// Register custom intervals and the callback on every request. The
		// activation hook alone is not persistent for custom intervals, and
		// without this callback WP-Cron has no handler to execute.
		add_filter( 'cron_schedules', array( $this->cron, 'register_intervals' ) );
		add_action( 'ics_cron_sync', array( $this->cron, 'run_sync' ) );
		add_action( 'init', array( $this->cron, 'schedule' ) );

		if ( is_admin() ) {
			$this->admin   = new ICS_Admin( $this->settings, $this->client, $this->logger, $this->mapping );
			$this->editor  = new ICS_Editor( $this->settings, $this->client );
			$this->updater = new ICS_Updater( $this->settings );
		}
	}
}
