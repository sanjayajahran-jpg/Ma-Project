<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Admin {

	private $settings;
	private $client;
	private $logger;
	private $mapping;

	public function __construct( $settings, $client, $logger, $mapping ) {
		$this->settings = $settings;
		$this->client   = $client;
		$this->logger   = $logger;
		$this->mapping  = $mapping;

		add_action( 'admin_menu', array( $this, 'register_menu' ) );
		add_action( 'admin_init', array( $this, 'register_settings' ) );
		add_action( 'admin_post_ics_test_connection', array( $this, 'handle_test_connection' ) );
		add_action( 'admin_post_ics_manual_sync', array( $this, 'handle_manual_sync' ) );
		add_action( 'admin_post_ics_clear_logs', array( $this, 'handle_clear_logs' ) );
		add_action( 'admin_post_ics_force_check_update', array( $this, 'handle_force_check_update' ) );
		add_action( 'admin_post_ics_update_plugin', array( $this, 'handle_update_plugin' ) );
		add_action( 'admin_post_ics_create_topup', array( $this, 'handle_create_topup' ) );
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_assets' ) );
	}

	public function register_menu() {
		add_menu_page(
			__( 'Inova CMS', 'inova-cms-sync' ),
			__( 'Inova CMS', 'inova-cms-sync' ),
			'manage_options',
			'insight-cms',
			array( $this, 'render_settings_page' ),
			'dashicons-migrate',
			80
		);

		add_submenu_page(
			'insight-cms',
			__( 'Top Up Saldo', 'inova-cms-sync' ),
			__( 'Top Up Saldo', 'inova-cms-sync' ),
			'manage_options',
			'insight-cms-billing',
			array( $this, 'render_billing_page' )
		);

		add_submenu_page(
			'insight-cms',
			__( 'Pengaturan', 'inova-cms-sync' ),
			__( 'Pengaturan', 'inova-cms-sync' ),
			'manage_options',
			'insight-cms',
			array( $this, 'render_settings_page' )
		);

		add_submenu_page(
			'insight-cms',
			__( 'Riwayat', 'inova-cms-sync' ),
			__( 'Riwayat', 'inova-cms-sync' ),
			'manage_options',
			'insight-cms-logs',
			array( $this, 'render_logs_page' )
		);

		add_submenu_page(
			'insight-cms',
			__( 'Status', 'inova-cms-sync' ),
			__( 'Status', 'inova-cms-sync' ),
			'manage_options',
			'insight-cms-status',
			array( $this, 'render_status_page' )
		);
	}

	public function register_settings() {
		register_setting( 'ics_settings_group', 'ics_settings', array( $this, 'sanitize_settings' ) );
	}

	public function sanitize_settings( $input ) {
		return $this->settings->save_all( $input );
	}

	public function enqueue_assets( $hook ) {
		if ( strpos( $hook, 'insight-cms' ) === false ) {
			return;
		}
		wp_enqueue_style( 'ics-admin', ICS_PLUGIN_URL . 'admin/css/ics-admin.css', array(), ICS_VERSION );
		wp_enqueue_script( 'ics-admin', ICS_PLUGIN_URL . 'admin/js/ics-admin.js', array( 'jquery' ), ICS_VERSION, true );
	}

	public function render_settings_page() {
		$s = $this->settings->get_all();
		include ICS_PLUGIN_DIR . 'admin/views/settings.php';
	}

	public function render_logs_page() {
		$type_filter = isset( $_GET['log_type'] ) ? sanitize_text_field( $_GET['log_type'] ) : '';
		$paged = isset( $_GET['paged'] ) ? max( 1, (int) $_GET['paged'] ) : 1;
		$per_page = 50;
		$offset = ( $paged - 1 ) * $per_page;

		$logs = $this->logger->get_logs( $per_page, $offset, $type_filter );
		$total = $this->logger->count_logs( $type_filter );
		$pages = ceil( $total / $per_page );

		include ICS_PLUGIN_DIR . 'admin/views/logs.php';
	}

	public function render_status_page() {
		$mapping_stats = $this->mapping->get_stats();
		$last_sync = get_option( 'ics_last_sync', '' );
		$cursor = get_option( 'ics_sync_cursor', '' );
		$next_cron = wp_next_scheduled( 'ics_cron_sync' );
		$cron_disabled = defined( 'DISABLE_WP_CRON' ) && DISABLE_WP_CRON;
		$configured = $this->settings->is_configured();

		include ICS_PLUGIN_DIR . 'admin/views/status.php';
	}

	public function render_billing_page() {
		$methods_response = $this->client->get_payment_methods( 100000 );
		$methods = array();
		$billing_error = '';
		if ( is_wp_error( $methods_response ) ) {
			$billing_error = $methods_response->get_error_message();
		} else {
			$body = json_decode( wp_remote_retrieve_body( $methods_response ), true );
			$methods = isset( $body['items'] ) && is_array( $body['items'] ) ? $body['items'] : array();
		}
		$provider = $this->client->provider_billing_url();
		include ICS_PLUGIN_DIR . 'admin/views/billing.php';
	}

	public function handle_test_connection() {
		check_admin_referer( 'ics_test_connection' );
		$result = $this->client->test_connection();
		$redirect = add_query_arg( 'page', 'insight-cms', admin_url( 'admin.php' ) );

		if ( true === $result ) {
			$redirect = add_query_arg( 'ics_msg', 'connection_ok', $redirect );
		} else {
			$msg = is_wp_error( $result ) ? $result->get_error_message() : 'Gagal';
			$redirect = add_query_arg( array( 'ics_msg' => 'connection_fail', 'ics_err' => rawurlencode( $msg ) ), $redirect );
		}

		wp_redirect( $redirect );
		exit;
	}

	public function handle_manual_sync() {
		check_admin_referer( 'ics_manual_sync' );
		$redirect = add_query_arg( 'page', 'insight-cms-status', admin_url( 'admin.php' ) );

		$result = ics()->importer->sync_batch();

		if ( is_wp_error( $result ) ) {
			$redirect = add_query_arg( array( 'ics_msg' => 'sync_fail', 'ics_err' => rawurlencode( $result->get_error_message() ) ), $redirect );
		} else {
			$redirect = add_query_arg( array(
				'ics_msg' => 'sync_ok',
				'imported' => $result['imported'],
				'skipped' => $result['skipped'],
			), $redirect );
		}

		wp_redirect( $redirect );
		exit;
	}

	public function handle_clear_logs() {
		check_admin_referer( 'ics_clear_logs' );
		$this->logger->clear_all();
		wp_redirect( add_query_arg( array( 'page' => 'insight-cms-logs', 'ics_msg' => 'logs_cleared' ), admin_url( 'admin.php' ) ) );
		exit;
	}

	public function handle_force_check_update() {
		check_admin_referer( 'ics_force_check_update' );
		$redirect = add_query_arg( 'page', 'insight-cms', admin_url( 'admin.php' ) );

		ics()->updater->force_check();
		// `force_check()` refreshes the remote version cache, but the native
		// WordPress update transient is only populated when WP runs its update
		// request. Trigger that request here before reading the result.
		delete_site_transient( 'update_plugins' );
		wp_update_plugins();

		$transient = get_site_transient( 'update_plugins' );
		if ( $transient && isset( $transient->response[ ICS_PLUGIN_BASENAME ] ) ) {
			$redirect = add_query_arg( 'ics_msg', 'update_available', $redirect );
		} else {
			$redirect = add_query_arg( 'ics_msg', 'up_to_date', $redirect );
		}

		wp_redirect( $redirect );
		exit;
	}

	public function handle_update_plugin() {
		if ( ! current_user_can( 'update_plugins' ) ) {
			wp_die( esc_html__( 'Anda tidak memiliki izin untuk memperbarui plugin.', 'inova-cms-sync' ) );
		}
		check_admin_referer( 'ics_update_plugin' );

		require_once ABSPATH . 'wp-admin/includes/file.php';
		require_once ABSPATH . 'wp-admin/includes/plugin.php';
		require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
		require_once ABSPATH . 'wp-admin/includes/class-plugin-upgrader.php';
		require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader-skin.php';
		require_once ABSPATH . 'wp-admin/includes/class-plugin-upgrader-skin.php';

		// Refresh the native transient so Plugin_Upgrader receives the package
		// URL supplied by our updater filter.
		delete_site_transient( 'update_plugins' );
		wp_update_plugins();

		$skin    = new Plugin_Upgrader_Skin();
		$upgrader = new Plugin_Upgrader( $skin );
		$result  = $upgrader->upgrade( ICS_PLUGIN_BASENAME, array( 'clear_destination' => true ) );
		$redirect = add_query_arg( 'page', 'insight-cms', admin_url( 'admin.php' ) );

		if ( is_wp_error( $result ) || ! $result ) {
			$message = is_wp_error( $result ) ? $result->get_error_message() : 'Update gagal diproses.';
			$redirect = add_query_arg( array( 'ics_msg' => 'update_fail', 'ics_err' => rawurlencode( $message ) ), $redirect );
		} else {
			$redirect = add_query_arg( 'ics_msg', 'update_success', $redirect );
		}

		wp_redirect( $redirect );
		exit;
	}

	public function handle_create_topup() {
		check_admin_referer( 'ics_create_topup' );
		$redirect = add_query_arg( 'page', 'insight-cms-billing', admin_url( 'admin.php' ) );
		$amount = isset( $_POST['amount'] ) ? absint( $_POST['amount'] ) : 0;
		$method = isset( $_POST['payment_method'] ) ? sanitize_text_field( wp_unslash( $_POST['payment_method'] ) ) : '';
		$user = wp_get_current_user();
		$response = $this->client->create_topup( $amount, $method, $user->user_email );
		if ( is_wp_error( $response ) ) {
			$redirect = add_query_arg( array( 'ics_msg' => 'topup_fail', 'ics_err' => rawurlencode( $response->get_error_message() ) ), $redirect );
			wp_safe_redirect( $redirect );
			exit;
		}
		$body = json_decode( wp_remote_retrieve_body( $response ), true );
		$payment_url = isset( $body['paymentUrl'] ) ? esc_url_raw( $body['paymentUrl'] ) : '';
		if ( $payment_url ) {
			wp_redirect( $payment_url );
			exit;
		}
		$redirect = add_query_arg( 'ics_msg', 'topup_created', $redirect );
		wp_safe_redirect( $redirect );
		exit;
	}
}
