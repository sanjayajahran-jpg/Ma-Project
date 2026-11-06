<?php
if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * HMAC-signed HTTP client for Inova CMS Open API.
 *
 * Auth protocol:
 *   X-AIV-Access-Key:    oak_...
 *   X-AIV-Timestamp:     RFC3339 without milliseconds (e.g. 2026-08-07T10:00:00Z)
 *   X-AIV-Nonce:         UUID v4
 *   X-AIV-Content-SHA256: hex( SHA-256(body) ) — empty body for GET
 *   X-AIV-Signature:     hex( HMAC-SHA256(secret, canonicalString) )
 *
 * Canonical string (joined by \n):
 *   METHOD
 *   /path
 *   canonical_query   (key=value pairs sorted by key then value, re-encoded; empty = "")
 *   timestamp
 *   nonce
 *   content_sha256
 */
class ICS_Client {

	private $settings;
	private $timeout = 45;

	public function __construct( ICS_Settings $settings ) {
		$this->settings = $settings;
	}

	public function get( $path, $query = array() ) {
		return $this->request( 'GET', $path, $query );
	}

	public function post( $path, $body = array() ) {
		return $this->request( 'POST', $path, array(), $body );
	}

	public function get_payment_methods( $amount = 100000 ) {
		return $this->get( '/billing/payment-methods', array( 'amount' => max( 10000, (int) $amount ) ) );
	}

	public function create_topup( $amount, $payment_method, $customer_email = '' ) {
		return $this->post( '/billing/topup', array(
			'amount'         => max( 10000, (int) $amount ),
			'paymentMethod'  => sanitize_text_field( $payment_method ),
			'customerEmail'  => sanitize_email( $customer_email ),
		) );
	}

	public function provider_billing_url() {
		$base = strtolower( (string) $this->settings->get( 'api_base_url', '' ) );
		if ( false !== strpos( $base, 'api-gt.inova.id' ) || false !== strpos( $base, 'api.groovetimes.com' ) ) {
			return array( 'label' => 'CMS Inova', 'url' => 'https://cms.inova.id/billing' );
		}
		if ( false !== strpos( $base, 'api-cms.bukin.id' ) || false !== strpos( $base, 'api.indosatu' ) ) {
			return array( 'label' => 'Linkup / Indosatu', 'url' => 'https://editor.indosatumedia.com/billing' );
		}
		return array( 'label' => 'CMS Inova', 'url' => 'https://editor.inova.id/billing' );
	}

	public function test_connection() {
		if ( ! $this->settings->is_configured() ) {
			$missing = $this->settings->get_config_error();
			return new WP_Error(
				'not_configured',
				sprintf( __( 'Field belum lengkap: %s', 'inova-cms-sync' ), implode( ', ', $missing ) )
			);
		}
		$response = $this->get( '/health' );
		if ( is_wp_error( $response ) ) {
			return $response;
		}
		$body = json_decode( wp_remote_retrieve_body( $response ), true );
		if ( isset( $body['ok'] ) && $body['ok'] ) {
			return true;
		}
		return new WP_Error( 'unexpected', __( 'Respons tidak terduga dari server.', 'inova-cms-sync' ) );
	}

	private function request( $method, $path, $query = array(), $body = array() ) {
		$settings = $this->settings->get_all();
		$base_url = rtrim( $settings['api_base_url'], '/' );
		$access_key = $settings['access_key'];
		$secret     = $settings['secret'];

		// Accept all documented forms: domain, /api/v1, or /openapi/v1.
		// The signed path must be identical to the actual request path.
		if ( preg_match( '#/api/v\d+$#', $base_url ) ) {
			$base_url = preg_replace( '#/api/v\d+$#', '/openapi/v1', $base_url );
		} elseif ( ! preg_match( '#/openapi/v\d+$#', $base_url ) ) {
			$base_url .= '/openapi/v1';
		}

		$path = '/' . ltrim( $path, '/' );

		// Server memvalidasi tanda tangan terhadap PATH LENGKAP request
		// (`/openapi/v1/...`), bukan path relatif yang dipakai untuk
		// menyusun URL. Tanpa prefiks ini, server menghitung tanda tangan
		// berbeda dan menolak setiap permintaan dengan INVALID_SIGNATURE.
		$base_path = wp_parse_url( $base_url, PHP_URL_PATH );
		$signed_path = rtrim( (string) $base_path, '/' ) . $path;

		$body_str = '';
		if ( 'POST' === $method && ! empty( $body ) ) {
			$body_str = wp_json_encode( $body );
		}

		$content_sha = hash( 'sha256', $body_str );

		$timestamp = gmdate( 'Y-m-d\TH:i:s\Z' );
		$nonce     = wp_generate_uuid4();

		$canonical_query = $this->build_canonical_query( $query );
		$canonical = implode( "\n", array(
			$method,
			$signed_path,
			$canonical_query,
			$timestamp,
			$nonce,
			$content_sha,
		) );

		$signature = hash_hmac( 'sha256', $canonical, $secret );

		$headers = array(
			'X-AIV-Access-Key'     => $access_key,
			'X-AIV-Timestamp'      => $timestamp,
			'X-AIV-Nonce'          => $nonce,
			'X-AIV-Content-SHA256' => $content_sha,
			'X-AIV-Signature'      => $signature,
			'X-Plugin-Version'     => ICS_VERSION,
		);

		if ( 'POST' === $method ) {
			$headers['Content-Type'] = 'application/json';
		}

		$url = $base_url . $path;
		if ( ! empty( $query ) ) {
			// Keep the wire query encoding identical to the canonical query used
			// for HMAC verification. WordPress' build_query() may use a different
			// space/character encoding depending on the WP/PHP version.
			$url .= '?' . http_build_query( $query, '', '&', PHP_QUERY_RFC3986 );
		}

		$args = array(
			'method'  => $method,
			'headers' => $headers,
			'timeout' => $this->timeout,
		);

		if ( 'POST' === $method && $body_str ) {
			$args['body'] = $body_str;
		}

		$response = wp_remote_request( $url, $args );

		if ( is_wp_error( $response ) ) {
			return new WP_Error(
				'http_error',
				sprintf( __( 'Kesalahan koneksi: %s', 'inova-cms-sync' ), $response->get_error_message() )
			);
		}

		$code = wp_remote_retrieve_response_code( $response );
		if ( $code >= 400 ) {
			$resp_body = json_decode( wp_remote_retrieve_body( $response ), true );
			$message = isset( $resp_body['error']['message'] )
				? $resp_body['error']['message']
				: sprintf( __( 'HTTP %d', 'inova-cms-sync' ), $code );
			$error_code = isset( $resp_body['error']['code'] )
				? $resp_body['error']['code']
				: 'http_' . $code;
			return new WP_Error( $error_code, $message );
		}

		return $response;
	}

	private function build_canonical_query( $query ) {
		if ( empty( $query ) ) {
			return '';
		}

		$pairs = array();
		foreach ( $query as $key => $value ) {
			$pairs[] = array( (string) $key, (string) $value );
		}

		usort( $pairs, function( $a, $b ) {
			if ( $a[0] === $b[0] ) {
				return strcmp( $a[1], $b[1] );
			}
			return strcmp( $a[0], $b[0] );
		} );

		$sorted = array();
		foreach ( $pairs as $pair ) {
			$sorted[ $pair[0] ] = $pair[1];
		}

		return http_build_query( $sorted, '', '&', PHP_QUERY_RFC3986 );
	}

	public function get_body( $response ) {
		if ( is_wp_error( $response ) ) {
			return null;
		}
		return json_decode( wp_remote_retrieve_body( $response ), true );
	}
}
