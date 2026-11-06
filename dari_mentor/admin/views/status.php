<?php
if ( ! defined( 'ABSPATH' ) ) exit;
?>
<div class="wrap">
	<h1>Status</h1>

	<?php if ( isset( $_GET['ics_msg'] ) ) : ?>
		<?php if ( 'sync_ok' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-success is-dismissible">
				<p>Sinkron selesai: <?php echo (int) $_GET['imported']; ?> diimpor, <?php echo (int) $_GET['skipped']; ?> dilewati.</p>
			</div>
		<?php elseif ( 'sync_fail' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-error is-dismissible">
				<p>Sinkron gagal: <?php echo esc_html( rawurldecode( $_GET['ics_err'] ?? '' ) ); ?></p>
			</div>
		<?php endif; ?>
	<?php endif; ?>

	<div class="ics-stat-grid">
		<div class="ics-stat-card">
			<span class="ics-stat-label">Total Artikel Sinkron</span>
			<span class="ics-stat-value"><?php echo (int) $mapping_stats['total']; ?></span>
		</div>
		<div class="ics-stat-card">
			<span class="ics-stat-label">Dari Sinkron</span>
			<span class="ics-stat-value"><?php echo (int) $mapping_stats['sync']; ?></span>
		</div>
		<div class="ics-stat-card">
			<span class="ics-stat-label">Dari AI Writer</span>
			<span class="ics-stat-value"><?php echo (int) $mapping_stats['ai']; ?></span>
		</div>
		<div class="ics-stat-card">
			<span class="ics-stat-label">Sinkron Terakhir</span>
			<span class="ics-stat-value" style="font-size:1rem"><?php echo $last_sync ?: 'Belum pernah'; ?></span>
		</div>
	</div>

	<h2>Detail</h2>
	<table class="form-table" role="presentation">
		<tr>
			<th>Status Koneksi</th>
			<td>
				<?php if ( $configured ) : ?>
					<span style="color:#059669;font-weight:600;">Terkonfigurasi</span>
				<?php else : ?>
					<span style="color:#dc2626;font-weight:600;">Belum lengkap</span>
				<?php endif; ?>
			</td>
		</tr>
		<tr>
			<th>Cursor Sinkron</th>
			<td><code><?php echo esc_html( $cursor ?: 'Belum mulal' ); ?></code></td>
		</tr>
		<tr>
			<th>Jadwal Cron Berikutnya</th>
			<td>
				<?php if ( $next_cron ) : ?>
					<?php echo esc_html( gmdate( 'Y-m-d H:i:s', $next_cron ) ); ?> (<?php echo human_time_diff( $next_cron ); ?> lagi)
				<?php else : ?>
					<span style="color:#999;">Tidak terjadwal</span>
				<?php endif; ?>
			</td>
		</tr>
		<?php if ( $cron_disabled ) : ?>
			<tr>
				<th></th>
				<td>
					<div class="notice notice-warning inline" style="margin:0">
						<p><strong>WP-Cron dinonaktifkan!</strong> Pastikan real cron sudah disetup:<br>
						<code>*/15 * * * * curl -s <?php echo esc_url( site_url( '/wp-cron.php?doing_wp_cron' ) ); ?> > /dev/null 2>&amp;1</code></p>
					</div>
				</td>
			</tr>
		<?php endif; ?>
	</table>

	<p>
		<a href="<?php echo wp_nonce_url( admin_url( 'admin-post.php?action=ics_manual_sync' ), 'ics_manual_sync' ); ?>" class="button button-primary button-large">
			Sinkron Sekarang
		</a>
	</p>
</div>
