<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Settings {

	const OPTION_KEY = 'ics_settings';

	private $defaults = array(
		'api_base_url'        => '',
		'access_key'          => '',
		'secret'              => '',
		'portal_id'           => '',
		'sync_enabled'        => 0,
		'interval'            => '30min',
		'batch_size'          => 10,
		'default_status'      => 'publish',
		'default_author'      => 0,
		'default_category'    => 0,
		'import_media'        => 1,
		'import_inline_media' => 0,
		'category_map'        => array(),
		'lock_edited_posts'   => 1,
		'ai_enabled'          => 0,
		'ai_default_agent'    => '',
		'ai_auto_fill_title'  => 1,
		'ai_auto_fill_excerpt'=> 0,
	);

	private $cache = null;

	public function get_all() {
		if ( null === $this->cache ) {
			$saved = get_option( self::OPTION_KEY, array() );
			$this->cache = wp_parse_args( $saved, $this->defaults );
		}
		return $this->cache;
	}

	public function get( $key, $default = null ) {
		$all = $this->get_all();
		return isset( $all[ $key ] ) ? $all[ $key ] : $default;
	}

	public function update( $key, $value ) {
		$all = $this->get_all();
		$all[ $key ] = $value;
		$this->cache = $all;
		update_option( self::OPTION_KEY, $all );
	}

	/**
	 * Sanitasi input sebelum disimpan.
	 *
	 * PENTING: fungsi ini dipakai sebagai `sanitize_callback` untuk
	 * `register_setting()` (lihat ICS_Admin::sanitize_settings). Kontrak
	 * Settings API mengharuskan callback ini HANYA mengembalikan nilai yang
	 * sudah disanitasi — WordPress sendiri yang menyimpannya lewat
	 * `update_option()`.
	 *
	 * Versi lama memanggil `update_option( self::OPTION_KEY, ... )` di sini
	 * juga. Karena `update_option()` SELALU memanggil ulang sanitize_callback
	 * yang sama (`sanitize_option()`), itu memicu rekursi tak berhenti:
	 * simpan → sanitasi → simpan → sanitasi → ... sampai memori PHP habis dan
	 * situs menampilkan "Telah terjadi eror kritis". Ini terjadi pada SETIAP
	 * kali menyimpan Pengaturan lewat form wp-admin, tanpa kecuali.
	 */
	public function save_all( $data ) {
		$all = $this->get_all();

		$fields = array_keys( $this->defaults );
		foreach ( $fields as $field ) {
			if ( isset( $data[ $field ] ) ) {
				if ( 'secret' === $field && '' === $data[ $field ] ) {
					continue;
				}
				$all[ $field ] = $this->sanitize( $field, $data[ $field ] );
			} elseif ( in_array( $field, array( 'sync_enabled', 'import_media', 'import_inline_media', 'lock_edited_posts', 'ai_enabled', 'ai_auto_fill_title', 'ai_auto_fill_excerpt' ), true ) ) {
				$all[ $field ] = 0;
			}
		}

		// Gabungkan category_map_keys + category_map_vals (baris dinamis
		// dari UI) menjadi category_map. HARUS dibaca dari $data (input POST
		// mentah), BUKAN $all: 'category_map_keys'/'category_map_vals' sengaja
		// tidak didaftarkan di $defaults (keduanya cuma representasi
		// sementara di form, yang tersimpan hanya category_map hasil
		// gabungannya) — loop sanitasi di atas hanya memproses field yang ada
		// di $defaults, jadi $all tidak akan pernah berisi kedua key ini.
		if ( isset( $data['category_map_keys'] ) || isset( $data['category_map_vals'] ) ) {
			$keys = isset( $data['category_map_keys'] ) && is_array( $data['category_map_keys'] )
				? $data['category_map_keys'] : array();
			$vals = isset( $data['category_map_vals'] ) && is_array( $data['category_map_vals'] )
				? $data['category_map_vals'] : array();
			$map = array();
			foreach ( $keys as $i => $key ) {
				$key = sanitize_text_field( trim( $key ) );
				if ( $key !== '' ) {
					$map[ $key ] = isset( $vals[ $i ] ) ? (int) $vals[ $i ] : 0;
				}
			}
			$all['category_map'] = $map;
		}

		$this->cache = $all;
		return $all;
	}

	private function sanitize( $field, $value ) {
		switch ( $field ) {
			case 'api_base_url':
				return esc_url_raw( trim( $value ) );
			case 'access_key':
			case 'secret':
			case 'portal_id':
			case 'ai_default_agent':
				return sanitize_text_field( trim( $value ) );
			case 'batch_size':
				return max( 1, min( 100, (int) $value ) );
			case 'default_status':
				return in_array( $value, array( 'publish', 'draft', 'pending', 'private' ), true ) ? $value : 'publish';
			case 'default_author':
			case 'default_category':
				return (int) $value;
			case 'interval':
				return in_array( $value, array( '15min', '30min', '1hour', '6hour', '12hour', 'daily' ), true ) ? $value : '30min';
			case 'category_map':
				if ( ! is_array( $value ) ) return array();
				$clean = array();
				foreach ( $value as $k => $v ) {
					$clean[ sanitize_text_field( $k ) ] = (int) $v;
				}
				return $clean;
			// 'category_map_keys'/'category_map_vals' TIDAK dilewatkan lewat
			// sini — keduanya bukan field di $defaults, jadi tidak pernah
			// masuk ke switch ini. Ditangani langsung di save_all() karena
			// perlu digabung berpasangan (indeks-ke-indeks) menjadi satu
			// array category_map, bukan disanitasi satu-per-satu.
			default:
				return sanitize_text_field( $value );
		}
	}

	public function is_configured() {
		$base_url   = $this->get( 'api_base_url' );
		$access_key = $this->get( 'access_key' );
		$secret     = $this->get( 'secret' );
		return ! empty( $base_url ) && ! empty( $access_key ) && ! empty( $secret );
	}

	public function get_config_error() {
		$missing = array();
		if ( empty( $this->get( 'api_base_url' ) ) ) $missing[] = 'API Base URL';
		if ( empty( $this->get( 'access_key' ) ) ) $missing[] = 'Access Key';
		if ( empty( $this->get( 'secret' ) ) ) $missing[] = 'Secret';
		return $missing;
	}
}
