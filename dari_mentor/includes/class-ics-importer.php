<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class ICS_Importer {

	private $client;
	private $settings;
	private $media;
	private $mapping;
	private $logger;

	public function __construct(
		ICS_Client $client,
		ICS_Settings $settings,
		ICS_Media $media,
		ICS_Mapping $mapping,
		ICS_Logger $logger
	) {
		$this->client   = $client;
		$this->settings  = $settings;
		$this->media    = $media;
		$this->mapping  = $mapping;
		$this->logger   = $logger;
	}

	public function sync_batch( $max = null ) {
		if ( ! $this->settings->is_configured() ) {
			return new WP_Error( 'not_configured', 'Kredensial Open API belum lengkap.' );
		}

		$batch_size = $max ?: (int) $this->settings->get( 'batch_size', 10 );
		$cursor     = get_option( 'ics_sync_cursor', '' );
		$portal_id  = $this->settings->get( 'portal_id', '' );

		$query = array(
			'limit'    => $batch_size,
			'order_by' => 'updated_at',
			'include'  => 'contentHtml',
		);

		// WAJIB: tanpa ini, API mengembalikan artikel dari SEMUA portal milik
		// media company yang sama (server men-scope /articles berdasarkan
		// media_company_id, portal_id hanya penyaring opsional). Satu media
		// company lazim menaungi beberapa portal — tanpa filter ini, artikel
		// portal lain bisa ikut ter-import ke situs WordPress yang salah.
		if ( $portal_id ) {
			$query['portal_id'] = $portal_id;
		}

		if ( $cursor ) {
			$query['updated_after'] = $cursor;
		}

		$response = $this->client->get( '/articles', $query );
		if ( is_wp_error( $response ) ) {
			return $response;
		}

		$body = $this->client->get_body( $response );
		// API mengembalikan field "items", bukan "articles".
		$articles = isset( $body['items'] ) ? $body['items'] : array();
		$imported = 0;
		$skipped  = 0;
		$latest_updated = '';

		foreach ( $articles as $article ) {
			$remote_id    = $article['id'];
			$updated_at   = isset( $article['updatedAt'] ) ? $article['updatedAt'] : '';
			$latest_updated = max( $latest_updated, $updated_at );

			$existing_post_id = $this->mapping->get_wp_post_id( $remote_id );
			$existing_updated = $this->mapping->get_remote_updated_at( $remote_id );

			// Older plugin versions could create the same article more than once
			// when the remote mapping was missing. Reuse an existing WordPress
			// post with the exact same title before inserting a new one.
			if ( ! $existing_post_id && ! empty( $article['title'] ) ) {
				$existing_post_id = $this->find_post_by_title( $article['title'] );
			}

			if ( $existing_post_id && $existing_updated === $updated_at ) {
				if ( $this->settings->get( 'lock_edited_posts' ) && get_post_meta( $existing_post_id, '_ics_edited_locally', true ) ) {
					$skipped++;
					continue;
				}
			}

			$post_id = $this->create_or_update_post( $article, $existing_post_id );

			if ( $post_id && ! is_wp_error( $post_id ) ) {
				$this->mapping->save_mapping( $remote_id, $post_id, $updated_at, 'sync' );
				$this->logger->log( $remote_id, $post_id, 'sync', 'success', sprintf( 'Sinkron: %s', $article['title'] ) );
				$imported++;
			} else {
				$error_msg = is_wp_error( $post_id ) ? $post_id->get_error_message() : 'Unknown error';
				$this->logger->log( $remote_id, 0, 'sync', 'failed', $error_msg );
			}
		}

		if ( $latest_updated ) {
			update_option( 'ics_sync_cursor', $latest_updated );
		}

		update_option( 'ics_last_sync', current_time( 'mysql' ) );

		return array(
			'imported' => $imported,
			'skipped'  => $skipped,
			'total'    => count( $articles ),
			'cursor'   => $latest_updated,
		);
	}

	private function find_post_by_title( $title ) {
		$posts = get_posts( array(
			'post_type'      => 'post',
			'post_status'    => array( 'publish', 'draft', 'pending', 'future', 'private' ),
			'title'          => wp_strip_all_tags( (string) $title ),
			'posts_per_page' => 1,
			'orderby'        => 'ID',
			'order'          => 'ASC',
			'fields'         => 'ids',
		) );

		return ! empty( $posts ) ? (int) $posts[0] : 0;
	}

	private function create_or_update_post( $article, $existing_post_id = 0 ) {
		$title       = isset( $article['title'] ) ? $article['title'] : '';
		$content_html = isset( $article['contentHtml'] ) ? $article['contentHtml'] : '';
		$excerpt     = isset( $article['excerpt'] ) ? $article['excerpt'] : '';
		$published   = isset( $article['publishedAt'] ) ? $article['publishedAt'] : '';
		$author_name = isset( $article['author']['name'] ) ? $article['author']['name'] : '';

		if ( empty( $content_html ) && isset( $article['content'] ) ) {
			$content_html = '<p>' . esc_html( $article['content'] ) . '</p>';
		}

		$post_data = array(
			'post_title'   => $title,
			'post_content' => $content_html,
			'post_excerpt' => $excerpt,
			'post_status'  => $this->settings->get( 'default_status', 'publish' ),
			'post_author'  => $this->resolve_author( $author_name ),
			'post_type'    => 'post',
		);

		if ( $published ) {
			$dt = strtotime( $published );
			if ( $dt ) {
				$post_data['post_date']     = gmdate( 'Y-m-d H:i:s', $dt );
				$post_data['post_date_gmt'] = gmdate( 'Y-m-d H:i:s', $dt );
			}
		}

		if ( $existing_post_id ) {
			$post_data['ID'] = $existing_post_id;
			$post_id = wp_update_post( $post_data, true );
		} else {
			$post_id = wp_insert_post( $post_data, true );
		}

		if ( is_wp_error( $post_id ) ) {
			return $post_id;
		}

		update_post_meta( $post_id, '_ics_remote_article_id', $article['id'] );
		if ( isset( $article['updatedAt'] ) ) {
			update_post_meta( $post_id, '_ics_remote_updated_at', $article['updatedAt'] );
		}

		$this->assign_categories( $post_id, $article );
		$this->assign_tags( $post_id, $article );

		$featured_url = isset( $article['featuredMedia']['url'] ) ? $article['featuredMedia']['url'] : '';
		if ( $featured_url && $this->settings->get( 'import_media' ) ) {
			$alt = isset( $article['featuredMedia']['alt'] ) ? $article['featuredMedia']['alt'] : '';
			$this->media->import_featured_image( $post_id, $featured_url, $alt, $title );
		}

		$content_html = $this->media->import_inline_images( $post_id, $content_html );
		if ( $content_html !== $post_data['post_content'] ) {
			wp_update_post( array( 'ID' => $post_id, 'post_content' => $content_html ) );
		}

		return $post_id;
	}

	private function resolve_author( $author_name ) {
		$default_author = (int) $this->settings->get( 'default_author', 0 );
		if ( $default_author ) {
			return $default_author;
		}
		if ( $author_name ) {
			$user = get_user_by( 'login', sanitize_title( $author_name ) );
			if ( $user ) {
				return $user->ID;
			}
		}
		$current_user = wp_get_current_user();
		return $current_user ? $current_user->ID : 1;
	}

	private function assign_categories( $post_id, $article ) {
		$category_map = $this->settings->get( 'category_map', array() );
		$cat_ids = array();

		$default_cat = (int) $this->settings->get( 'default_category', 0 );
		if ( $default_cat ) {
			$cat_ids[] = $default_cat;
		}

		if ( isset( $article['category']['slug'] ) ) {
			$remote_slug = $article['category']['slug'];
			if ( isset( $category_map[ $remote_slug ] ) && $category_map[ $remote_slug ] ) {
				$cat_ids[] = (int) $category_map[ $remote_slug ];
			} elseif ( isset( $article['category']['name'] ) ) {
				$cat = get_term_by( 'name', $article['category']['name'], 'category' );
				if ( ! $cat ) {
					$result = wp_insert_term( $article['category']['name'], 'category' );
					if ( ! is_wp_error( $result ) ) {
						$cat_ids[] = (int) $result['term_id'];
					}
				} else {
					$cat_ids[] = (int) $cat->term_id;
				}
			}
		}

		if ( ! empty( $cat_ids ) ) {
			wp_set_post_categories( $post_id, array_unique( $cat_ids ) );
		}
	}

	private function assign_tags( $post_id, $article ) {
		$tag_slugs = array();
		if ( isset( $article['tags'] ) && is_array( $article['tags'] ) ) {
			foreach ( $article['tags'] as $tag ) {
				$tag_slugs[] = isset( $tag['slug'] ) ? $tag['slug'] : ( isset( $tag['name'] ) ? sanitize_title( $tag['name'] ) : '' );
			}
		}
		if ( ! empty( $tag_slugs ) ) {
			wp_set_post_tags( $post_id, array_filter( $tag_slugs ), false );
		}
	}
}
