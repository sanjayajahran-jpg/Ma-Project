<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Media {

	private $client;
	private $settings;

	public function __construct( ICS_Client $client, ICS_Settings $settings ) {
		$this->client   = $client;
		$this->settings = $settings;
	}

	public function import_featured_image( $post_id, $media_url, $alt = '', $title = '' ) {
		if ( empty( $media_url ) ) {
			return false;
		}

		$existing = get_post_meta( $post_id, '_ics_featured_url', true );
		if ( $existing === $media_url ) {
			return (int) get_post_thumbnail_id( $post_id );
		}

		if ( ! function_exists( 'media_sideload_image' ) ) {
			require_once ABSPATH . 'wp-admin/includes/file.php';
			require_once ABSPATH . 'wp-admin/includes/media.php';
			require_once ABSPATH . 'wp-admin/includes/image.php';
		}

		$attachment_id = media_sideload_image( $media_url, $post_id, $title ?: $alt, 'id' );

		if ( is_wp_error( $attachment_id ) ) {
			return false;
		}

		set_post_thumbnail( $post_id, $attachment_id );

		if ( $alt ) {
			update_post_meta( $attachment_id, '_wp_attachment_image_alt', $alt );
		}

		update_post_meta( $post_id, '_ics_featured_url', $media_url );

		return $attachment_id;
	}

	public function import_inline_images( $post_id, $html ) {
		if ( ! $this->settings->get( 'import_inline_media' ) ) {
			return $html;
		}

		$pattern = '/<img[^>]+src=["\']([^"\']+)["\'][^>]*>/i';
		if ( ! preg_match_all( $pattern, $html, $matches ) ) {
			return $html;
		}

		if ( ! function_exists( 'media_sideload_image' ) ) {
			require_once ABSPATH . 'wp-admin/includes/file.php';
			require_once ABSPATH . 'wp-admin/includes/media.php';
			require_once ABSPATH . 'wp-admin/includes/image.php';
		}

		foreach ( $matches[1] as $old_url ) {
			if ( strpos( $old_url, home_url() ) === 0 ) {
				continue;
			}

			$attachment_id = media_sideload_image( $old_url, $post_id, '', 'id' );
			if ( is_wp_error( $attachment_id ) ) {
				continue;
			}

			$new_url = wp_get_attachment_url( $attachment_id );
			if ( $new_url ) {
				$html = str_replace( $old_url, $new_url, $html );
			}
		}

		return $html;
	}
}
