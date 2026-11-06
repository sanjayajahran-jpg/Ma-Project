<?php
if ( ! defined( 'ABSPATH' ) ) exit;
?>
<div class="wrap">
	<h1>Riwayat Sinkronisasi</h1>

	<?php if ( isset( $_GET['ics_msg'] ) && 'logs_cleared' === $_GET['ics_msg'] ) : ?>
		<div class="notice notice-success is-dismissible"><p>Log dibersihkan.</p></div>
	<?php endif; ?>

	<div class="tablenav top">
		<div class="alignleft actions">
			<a href="<?php echo esc_url( add_query_arg( 'log_type', '', $_SERVER['REQUEST_URI'] ) ); ?>" class="button <?php echo empty( $type_filter ) ? 'button-primary' : ''; ?>">Semua</a>
			<a href="<?php echo esc_url( add_query_arg( 'log_type', 'sync', $_SERVER['REQUEST_URI'] ) ); ?>" class="button <?php echo 'sync' === $type_filter ? 'button-primary' : ''; ?>">Sync</a>
			<a href="<?php echo esc_url( add_query_arg( 'log_type', 'ai', $_SERVER['REQUEST_URI'] ) ); ?>" class="button <?php echo 'ai' === $type_filter ? 'button-primary' : ''; ?>">AI</a>
		</div>
		<div class="alignright">
			<a href="<?php echo wp_nonce_url( admin_url( 'admin-post.php?action=ics_clear_logs' ), 'ics_clear_logs' ); ?>" class="button button-link-delete" onclick="return confirm('Hapus semua log?')">Bersihkan Log</a>
		</div>
	</div>

	<table class="wp-list-table widefat fixed striped">
		<thead>
			<tr>
				<th style="width:150px">Waktu</th>
				<th style="width:60px">Jenis</th>
				<th style="width:60px">Status</th>
				<th>Artikel</th>
				<th>Pesan</th>
				<th style="width:80px">Post WP</th>
			</tr>
		</thead>
		<tbody>
			<?php if ( empty( $logs ) ) : ?>
				<tr><td colspan="6" style="text-align:center;color:#999;">Belum ada catatan.</td></tr>
			<?php else : ?>
				<?php foreach ( $logs as $log ) : ?>
					<tr>
						<td><?php echo esc_html( $log->created_at ); ?></td>
						<td>
							<span class="ics-badge ics-badge-<?php echo esc_attr( $log->type ); ?>">
								<?php echo 'sync' === $log->type ? 'Sync' : 'AI'; ?>
							</span>
						</td>
						<td>
							<span style="color: <?php echo 'failed' === $log->status ? '#dc2626' : '#059669'; ?>; font-weight:600;">
								<?php echo esc_html( ucfirst( $log->status ) ); ?>
							</span>
						</td>
						<td><?php echo esc_html( $log->message ); ?></td>
						<td style="font-size:0.85em;color:#666;font-family:monospace"><?php echo esc_html( substr( $log->remote_article_id, 0, 12 ) ); ?></td>
						<td>
							<?php if ( $log->wp_post_id ) : ?>
								<a href="<?php echo esc_url( get_edit_post_link( $log->wp_post_id ) ); ?>" target="_blank">#<?php echo (int) $log->wp_post_id; ?></a>
							<?php endif; ?>
						</td>
					</tr>
				<?php endforeach; ?>
			<?php endif; ?>
		</tbody>
	</table>

	<?php if ( $pages > 1 ) : ?>
		<div class="tablenav bottom">
			<div class="tablenav-pages">
				<?php
				echo paginate_links( array(
					'base'      => add_query_arg( 'paged', '%#%' ),
					'format'    => '',
					'current'   => $paged,
					'total'     => $pages,
					'prev_text' => '&laquo;',
					'next_text' => '&raquo;',
				) );
				?>
			</div>
		</div>
	<?php endif; ?>
</div>
