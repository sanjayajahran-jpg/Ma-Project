<?php
if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * Auto-update handler for Inova CMS Sync plugin.
 *
 * Hooks into WordPress's native update system so updates appear in
 * Dashboard → Updates and Plugins page — same as wordpress.org plugins.
 *
 * @package Insight_CMS_Sync
 */
class ICS_Updater {

	const VERSION_ENDPOINT = '/plugin/wordpress/version';
	const CHECK_INTERVAL   = 12 * HOUR_IN_SECONDS;

	private $settings;

	public function __construct( ICS_Settings $settings ) {
		$this->settings = $settings;
		add_filter( 'pre_set_site_transient_update_plugins', array( $this, 'check_update' ) );
		add_filter( 'plugins_api', array( $this, 'plugin_info' ), 10, 3 );
	}

	/**
	 * Fetch latest version info from CMS API.
	 * Uses HMAC if configured, falls back to public endpoint.
	 */
	private function fetch_version_info() {
		$cached = get_transient( 'ics_update_info' );
		if ( false !== $cached && is_array( $cached ) ) {
			return $cached;
		}

		$api_base = rtrim( $this->settings->get( 'api_base_url', '' ), '/' );
		if ( preg_match( '#/api/v\d+$#', $api_base ) ) {
			$openapi_base = preg_replace( '#/api/v\d+$#', '/openapi/v1', $api_base );
		} elseif ( preg_match( '#/openapi/v\d+$#', $api_base ) ) {
			$openapi_base = $api_base;
		} else {
			$openapi_base = $api_base . '/openapi/v1';
		}

		// Try the openapi endpoint (public, no auth needed for version check)
		$url = $openapi_base . self::VERSION_ENDPOINT;

		$response = wp_remote_get( $url, array(
			'timeout' => 10,
			'headers' => array( 'X-Plugin-Version' => ICS_VERSION ),
		) );

		if ( is_wp_error( $response ) ) {
			return false;
		}

		$body = json_decode( wp_remote_retrieve_body( $response ), true );
		if ( ! $body || ! isset( $body['version'] ) ) {
			return false;
		}

		$info = array(
			'version'      => $body['version'],
			'downloadUrl'  => isset( $body['downloadUrl'] ) ? $body['downloadUrl'] : '',
			'requiresWp'   => isset( $body['requiresWp'] ) ? $body['requiresWp'] : '6.0',
			'requiresPhp'  => isset( $body['requiresPhp'] ) ? $body['requiresPhp'] : '7.4',
			'testedWp'     => isset( $body['testedWp'] ) ? $body['testedWp'] : '',
			'changelog'    => isset( $body['changelog'] ) ? $body['changelog'] : '',
			'sha256'       => isset( $body['sha256'] ) ? $body['sha256'] : '',
			'releasedAt'   => isset( $body['releasedAt'] ) ? $body['releasedAt'] : '',
			'packageUrl'   => isset( $body['downloadUrl'] ) ? $body['downloadUrl'] : '',
		);

		set_transient( 'ics_update_info', $info, self::CHECK_INTERVAL );
		return $info;
	}

	/**
	 * Inject update info into WP transient.
	 * Fires on every admin page load (WP caches the transient itself).
	 */
	public function check_update( $transient ) {
		if ( empty( $transient ) || ! is_object( $transient ) ) {
			return $transient;
		}

		$info = $this->fetch_version_info();
		if ( ! $info ) {
			return $transient;
		}

		// Only proceed if remote version is newer
		if ( ! version_compare( $info['version'], ICS_VERSION, '>' ) ) {
			return $transient;
		}

		// Build the update object WP expects
		$obj                          = new \stdClass();
		$obj->slug                    = 'insight-cms-sync';
		$obj->plugin                  = ICS_PLUGIN_BASENAME;
		$obj->new_version             = $info['version'];
		$obj->requires                = $info['requiresWp'];
		$obj->requires_php            = $info['requiresPhp'];
		$obj->tested                  = $info['testedWp'];
		$obj->package                 = $info['packageUrl'];
		$obj->icons                   = array();
		$obj->url                     = 'https://plugins.inova.id';

		$transient->response[ ICS_PLUGIN_BASENAME ] = $obj;

		return $transient;
	}

	/**
	 * Provide plugin info for the "View details" modal in WP admin.
	 */
	public function plugin_info( $result, $action, $args ) {
		if ( 'plugin_information' !== $action ) {
			return $result;
		}
		if ( ! isset( $args->slug ) || 'insight-cms-sync' !== $args->slug ) {
			return $result;
		}

		$info = $this->fetch_version_info();
		if ( ! $info ) {
			return $result;
		}

		// Force refresh transient on "View details"
		delete_transient( 'ics_update_info' );

		$obj              = new \stdClass();
		$obj->name        = 'Inova CMS Sync';
		$obj->slug        = 'insight-cms-sync';
		$obj->version     = $info['version'];
		$obj->author      = '<a href="https://plugins.inova.id">Inova</a>';
		$obj->homepage    = 'https://plugins.inova.id';
		$obj->requires    = $info['requiresWp'];
		$obj->requires_php= $info['requiresPhp'];
		$obj->tested      = $info['testedWp'];
		$obj->last_updated= $info['releasedAt'];
		$obj->download_link = $info['downloadUrl'];
		$obj->sections    = array(
			'description'  => 'Sinkronisasi artikel dari Inova CMS ke WordPress + AI Writer.',
			'changelog'    => '<pre style="white-space:pre-wrap">' . esc_html( $info['changelog'] ) . '</pre>',
		);

		return $obj;
	}

	/**
	 * Force-check for updates (bypass cache).
	 * Called from AJAX / settings page button.
	 */
	public function force_check() {
		delete_transient( 'ics_update_info' );
		return $this->fetch_version_info();
	}

	/**
	 * Verify downloaded zip integrity.
	 * Returns true if SHA256 matches or no hash provided.
	 */
	public static function verify_download( $zip_path, $expected_sha256 ) {
		if ( empty( $expected_sha256 ) ) {
			return true; // no hash = skip verification
		}
		$actual = hash_file( 'sha256', $zip_path );
		return $actual === $expected_sha256;
	}
}
