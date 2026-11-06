<?php
if ( ! defined( 'ABSPATH' ) ) exit;

/**
 * F2: AI Writer — inject button into post editor + AJAX handlers.
 */
class ICS_Editor {

	private $settings;
	private $client;

	public function __construct( $settings, $client ) {
		$this->settings = $settings;
		$this->client   = $client;

		add_action( 'admin_enqueue_scripts', array( $this, 'maybe_enqueue' ) );
		add_action( 'media_buttons', array( $this, 'classic_editor_button' ) );
		add_action( 'admin_footer', array( $this, 'render_modal' ) );

		add_action( 'wp_ajax_ics_ai_generate', array( $this, 'ajax_generate' ) );
		add_action( 'wp_ajax_ics_ai_poll', array( $this, 'ajax_poll' ) );
		add_action( 'wp_ajax_ics_ai_get_article', array( $this, 'ajax_get_article' ) );
	}

	public function maybe_enqueue( $hook ) {
		if ( ! in_array( $hook, array( 'post.php', 'post-new.php' ), true ) ) {
			return;
		}
		if ( ! $this->should_show_button() ) {
			return;
		}

		wp_enqueue_style( 'ics-ai-modal', ICS_PLUGIN_URL . 'admin/css/ics-ai-modal.css', array(), ICS_VERSION );
		wp_enqueue_script( 'ics-ai-core', ICS_PLUGIN_URL . 'admin/js/ics-ai-core.js', array( 'jquery' ), ICS_VERSION, true );

		$ai_enabled = (bool) $this->settings->get( 'ai_enabled' );
		$agents = $this->get_cached_agents();

		wp_localize_script( 'ics-ai-core', 'icsAi', array(
			'ajaxUrl'   => admin_url( 'admin-ajax.php' ),
			'nonce'     => wp_create_nonce( 'ics_ai_nonce' ),
			'enabled'   => $ai_enabled,
			'agents'    => $agents,
			'defaultAgent' => $this->settings->get( 'ai_default_agent' ),
			'autoFillTitle' => (bool) $this->settings->get( 'ai_auto_fill_title' ),
			'autoFillExcerpt' => (bool) $this->settings->get( 'ai_auto_fill_excerpt' ),
			'isBlockEditor' => $this->is_block_editor(),
			'credits'   => $this->get_cached_credits(),
		) );

		if ( $this->is_block_editor() ) {
			wp_enqueue_script( 'ics-ai-gutenberg', ICS_PLUGIN_URL . 'admin/js/ics-ai-gutenberg.js', array( 'ics-ai-core', 'wp-element', 'wp-data', 'wp-editor', 'wp-plugins' ), ICS_VERSION, true );
		} else {
			wp_enqueue_script( 'ics-ai-classic', ICS_PLUGIN_URL . 'admin/js/ics-ai-classic.js', array( 'ics-ai-core', 'jquery' ), ICS_VERSION, true );
		}
	}

	private function should_show_button() {
		if ( ! current_user_can( 'edit_posts' ) ) {
			return false;
		}
		if ( ! $this->settings->is_configured() ) {
			return false;
		}
		return (bool) $this->settings->get( 'ai_enabled' );
	}

	private function is_block_editor() {
		$screen = get_current_screen();
		if ( $screen && method_exists( $screen, 'is_block_editor' ) && $screen->is_block_editor() ) {
			return true;
		}
		if ( function_exists( 'use_block_editor_for_post' ) ) {
			global $post;
			if ( $post ) {
				return use_block_editor_for_post( $post );
			}
		}
		return false;
	}

	private function get_cached_agents() {
		$cached = get_transient( 'ics_agents_cache' );
		if ( false !== $cached && is_array( $cached ) ) {
			return $cached;
		}

		$response = $this->client->get( '/agents' );
		if ( is_wp_error( $response ) ) {
			return array();
		}

		$body = $this->client->get_body( $response );
		$agents = isset( $body['items'] ) ? $body['items'] : array();
		set_transient( 'ics_agents_cache', $agents, HOUR_IN_SECONDS );
		return $agents;
	}

	private function get_cached_credits() {
		$cached = get_transient( 'ics_credits_cache' );
		if ( false !== $cached ) {
			return $cached;
		}

		$response = $this->client->get( '/credits' );
		if ( is_wp_error( $response ) ) {
			return null;
		}

		$body = $this->client->get_body( $response );
		$balance = isset( $body['balance'] ) ? (int) $body['balance'] : null;
		set_transient( 'ics_credits_cache', $balance, 5 * MINUTE_IN_SECONDS );
		return $balance;
	}

	public function classic_editor_button() {
		if ( ! $this->should_show_button() || $this->is_block_editor() ) {
			return;
		}
		?>
		<button type="button" id="ics-ai-button" class="button" title="Inova AI Writer">
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:4px">
				<path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 16.8l-6.2 4.5 2.4-7.4L2 9.4h7.6z"/>
			</svg>
			Inova AI
		</button>
		<?php
	}

	public function render_modal() {
		$screen = get_current_screen();
		if ( ! $screen || ! in_array( $screen->base, array( 'post', 'edit' ), true ) ) {
			return;
		}
		if ( 'post' !== $screen->base ) {
			return;
		}
		if ( ! $this->should_show_button() ) {
			return;
		}
		include ICS_PLUGIN_DIR . 'admin/views/ai-modal.php';
	}

	public function ajax_generate() {
		check_ajax_referer( 'ics_ai_nonce', 'nonce' );
		if ( ! current_user_can( 'edit_posts' ) ) {
			wp_send_json_error( array( 'message' => 'Akses ditolak.' ), 403 );
		}

		$body = array(
			'title'     => sanitize_text_field( $_POST['title'] ?? '' ),
			'angle'     => sanitize_text_field( $_POST['angle'] ?? '' ),
			'keywords'  => sanitize_text_field( $_POST['keywords'] ?? '' ),
			'tone'      => sanitize_text_field( $_POST['tone'] ?? '' ),
			'instructions' => sanitize_textarea_field( $_POST['instructions'] ?? '' ),
			'source_url'=> esc_url_raw( $_POST['source_url'] ?? '' ),
			'agent_id'  => sanitize_text_field( $_POST['agent_id'] ?? '' ),
		);
		$body = array_filter( $body, fn( $v ) => '' !== $v );

		if ( empty( $body['title'] ) ) {
			wp_send_json_error( array( 'message' => 'Judul wajib diisi.' ), 400 );
		}

		$response = $this->client->post( '/ai/articles/generate', $body );
		if ( is_wp_error( $response ) ) {
			wp_send_json_error( array(
				'message' => $response->get_error_message(),
				'code'    => $response->get_error_code(),
			), 500 );
		}

		$result = $this->client->get_body( $response );
		wp_send_json_success( $result );
	}

	public function ajax_poll() {
		check_ajax_referer( 'ics_ai_nonce', 'nonce' );
		$job_id = sanitize_text_field( $_POST['job_id'] ?? '' );
		if ( ! $job_id ) {
			wp_send_json_error( array( 'message' => 'Job ID kosong.' ), 400 );
		}

		$response = $this->client->get( "/ai/generate-jobs/{$job_id}" );
		if ( is_wp_error( $response ) ) {
			wp_send_json_error( array( 'message' => $response->get_error_message() ), 500 );
		}

		wp_send_json_success( $this->client->get_body( $response ) );
	}

	public function ajax_get_article() {
		check_ajax_referer( 'ics_ai_nonce', 'nonce' );
		$article_id = sanitize_text_field( $_POST['article_id'] ?? '' );
		if ( ! $article_id ) {
			wp_send_json_error( array( 'message' => 'Article ID kosong.' ), 400 );
		}

		$response = $this->client->get( "/articles/{$article_id}", array( 'include' => 'contentHtml' ) );
		if ( is_wp_error( $response ) ) {
			wp_send_json_error( array( 'message' => $response->get_error_message() ), 500 );
		}

		$body = $this->client->get_body( $response );
		wp_send_json_success( $body );
	}
}
