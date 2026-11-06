<?php
if ( ! defined( 'ABSPATH' ) ) exit;
$s = $this->settings->get_all();
$users = get_users( array( 'number' => 50 ) );
$categories = get_categories( array( 'hide_empty' => false, 'number' => 50 ) );
?>
<div class="wrap">
	<h1>Inova CMS Sync &mdash; Pengaturan</h1>

	<?php if ( isset( $_GET['ics_msg'] ) ) : ?>
		<?php if ( 'connection_ok' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-success is-dismissible"><p>Koneksi berhasil!</p></div>
		<?php elseif ( 'connection_fail' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-error is-dismissible"><p>Koneksi gagal: <?php echo esc_html( rawurldecode( $_GET['ics_err'] ?? '' ) ); ?></p></div>
		<?php endif; ?>
	<?php endif; ?>

	<form method="post" action="options.php">
		<?php settings_fields( 'ics_settings_group' ); ?>

		<h2 class="title">Koneksi Open API</h2>
		<table class="form-table" role="presentation">
			<tr>
				<th><label for="api_base_url">API Base URL</label></th>
				<td><input type="url" id="api_base_url" name="ics_settings[api_base_url]" value="<?php echo esc_attr( $s['api_base_url'] ); ?>" class="regular-text" placeholder="https://api-cms.bukin.id/openapi/v1" /></td>
			</tr>
			<tr>
				<th><label for="access_key">Access Key</label></th>
				<td><input type="text" id="access_key" name="ics_settings[access_key]" value="<?php echo esc_attr( $s['access_key'] ); ?>" class="regular-text" placeholder="oak_..." /></td>
			</tr>
			<tr>
				<th><label for="secret">Secret</label></th>
				<td><input type="password" id="secret" name="ics_settings[secret]" value="" class="regular-text" placeholder="<?php echo $s['secret'] ? '•••• (kosongkan jika tidak diubah)' : ''; ?>" autocomplete="new-password" /></td>
			</tr>
			<tr>
				<th><label for="portal_id">Portal ID</label></th>
				<td><input type="text" id="portal_id" name="ics_settings[portal_id]" value="<?php echo esc_attr( $s['portal_id'] ); ?>" class="regular-text" placeholder="UUID portal" /></td>
			</tr>
			<tr>
				<th>Tes Koneksi</th>
				<td>
					<a href="<?php echo wp_nonce_url( admin_url( 'admin-post.php?action=ics_test_connection' ), 'ics_test_connection' ); ?>" class="button button-secondary">Tes Koneksi</a>
				</td>
			</tr>
		</table>

		<h2 class="title">Sinkronisasi Artikel (F1)</h2>
		<table class="form-table" role="presentation">
			<tr>
				<th>Aktifkan Sinkronisasi</th>
				<td><label><input type="checkbox" name="ics_settings[sync_enabled]" value="1" <?php checked( $s['sync_enabled'], 1 ); ?> /> Sinkron otomatis dari CMS ke WordPress</label></td>
			</tr>
			<tr>
				<th><label for="interval">Interval</label></th>
				<td>
					<select id="interval" name="ics_settings[interval]">
						<?php
						$intervals = array( '15min' => '15 Menit', '30min' => '30 Menit', '1hour' => '1 Jam', '6hour' => '6 Jam', '12hour' => '12 Jam', 'daily' => '1 Hari' );
						foreach ( $intervals as $k => $v ) :
						?>
							<option value="<?php echo esc_attr( $k ); ?>" <?php selected( $s['interval'], $k ); ?>><?php echo esc_html( $v ); ?></option>
						<?php endforeach; ?>
					</select>
				</td>
			</tr>
			<tr>
				<th><label for="batch_size">Jumlah per siklus</label></th>
				<td><input type="number" id="batch_size" name="ics_settings[batch_size]" value="<?php echo esc_attr( $s['batch_size'] ); ?>" min="1" max="100" class="small-text" /></td>
			</tr>
			<tr>
				<th><label for="default_status">Status Post</label></th>
				<td>
					<select id="default_status" name="ics_settings[default_status]">
						<option value="publish" <?php selected( $s['default_status'], 'publish' ); ?>>Publish</option>
						<option value="draft" <?php selected( $s['default_status'], 'draft' ); ?>>Draft</option>
						<option value="pending" <?php selected( $s['default_status'], 'pending' ); ?>>Pending Review</option>
					</select>
				</td>
			</tr>
			<tr>
				<th><label for="default_author">Penulis Default</label></th>
				<td>
					<select id="default_author" name="ics_settings[default_author]">
						<option value="0">Auto / User saat ini</option>
						<?php foreach ( $users as $user ) : ?>
							<option value="<?php echo esc_attr( $user->ID ); ?>" <?php selected( $s['default_author'], $user->ID ); ?>><?php echo esc_html( $user->display_name ); ?></option>
						<?php endforeach; ?>
					</select>
				</td>
			</tr>
			<tr>
				<th><label for="default_category">Kategori Default</label></th>
				<td>
					<select id="default_category" name="ics_settings[default_category]">
						<option value="0">Tidak ada</option>
						<?php foreach ( $categories as $cat ) : ?>
							<option value="<?php echo esc_attr( $cat->term_id ); ?>" <?php selected( $s['default_category'], $cat->term_id ); ?>><?php echo esc_html( $cat->name ); ?></option>
						<?php endforeach; ?>
					</select>
				</td>
			</tr>
			<tr>
				<th>Impor Media</th>
				<td>
					<label><input type="checkbox" name="ics_settings[import_media]" value="1" <?php checked( $s['import_media'], 1 ); ?> /> Impor featured image</label><br />
					<label><input type="checkbox" name="ics_settings[import_inline_media]" value="1" <?php checked( $s['import_inline_media'], 1 ); ?> /> Impor gambar inline (ganti URL ke domain WP)</label>
				</td>
			</tr>
			<tr>
				<th>Kunci setelah diedit</th>
				<td><label><input type="checkbox" name="ics_settings[lock_edited_posts]" value="1" <?php checked( $s['lock_edited_posts'], 1 ); ?> /> Jangan timpa post yang sudah diedit manual di WP</label></td>
			</tr>
		</table>

		<h2 class="title">Pemetaan Kategori</h2>
		<p class="description">Petakan kategori CMS ke kategori WordPress. Kosongkan untuk auto-create. Klik "Tambah Pemetaan" untuk menambah.</p>
		<table class="form-table" role="presentation">
			<tr>
				<th>Kategori CMS &rarr; WP</th>
				<td id="ics-category-map-list">
					<?php if ( ! empty( $s['category_map'] ) ) : ?>
						<?php foreach ( $s['category_map'] as $remote_slug => $wp_cat_id ) : ?>
							<div class="ics-map-row">
								<input type="text" name="ics_settings[category_map_keys][]" value="<?php echo esc_attr( $remote_slug ); ?>" placeholder="slug kategori CMS (mis. daerah)" class="regular-text" />
								&rarr;
								<select name="ics_settings[category_map_vals][]">
									<option value="0">Auto-create</option>
									<?php foreach ( $categories as $cat ) : ?>
										<option value="<?php echo esc_attr( $cat->term_id ); ?>" <?php selected( (int) $wp_cat_id, (int) $cat->term_id ); ?>><?php echo esc_html( $cat->name ); ?></option>
									<?php endforeach; ?>
								</select>
								<button type="button" class="button ics-map-remove" onclick="this.closest('.ics-map-row').remove()">&times;</button>
							</div>
						<?php endforeach; ?>
					<?php endif; ?>
					<div id="ics-map-empty" style="<?php echo empty( $s['category_map'] ) ? '' : 'display:none;'; ?>color:#666;font-style:italic;">Belum ada pemetaan. Klik tombol di bawah untuk menambah.</div>
				</td>
			</tr>
			<tr>
				<th></th>
				<td>
					<button type="button" class="button button-secondary" id="ics-add-mapping">+ Tambah Pemetaan</button>
				</td>
			</tr>
		</table>

		<script>
		jQuery(function($){
			var categories = <?php echo json_encode( array_map(function($c){ return array('id'=>$c->term_id,'name'=>$c->name); }, $categories) ); ?>;

			function newRow() {
				var opts = '<option value="0">Auto-create</option>';
				categories.forEach(function(c){
					opts += '<option value="'+c.id+'">'+c.name+'</option>';
				});
				var html = '<div class="ics-map-row" style="margin-bottom:6px">'
					+ '<input type="text" name="ics_settings[category_map_keys][]" value="" placeholder="slug kategori CMS (mis. daerah)" class="regular-text" />'
					+ ' &rarr; '
					+ '<select name="ics_settings[category_map_vals][]">' + opts + '</select>'
					+ ' <button type="button" class="button ics-map-remove" onclick="this.closest(\'.ics-map-row\').remove()">&times;</button>'
					+ '</div>';
				$('#ics-map-empty').hide();
				$('#ics-category-map-list').append(html);
			}

			$('#ics-add-mapping').on('click', newRow);
		});
		</script>

		<h2 class="title">Inova AI Writer (F2)</h2>
		<p class="description">Aktifkan tombol "Inova AI" di editor post untuk generate artikel dengan AI.</p>
		<table class="form-table" role="presentation">
			<tr>
				<th>Aktifkan AI Writer</th>
				<td><label><input type="checkbox" name="ics_settings[ai_enabled]" value="1" <?php checked( $s['ai_enabled'], 1 ); ?> /> Tampilkan tombol "Inova AI" di editor post</label></td>
			</tr>
			<tr>
				<th><label for="ai_default_agent">Agent Default</label></th>
				<td>
					<input type="text" id="ai_default_agent" name="ics_settings[ai_default_agent]" value="<?php echo esc_attr( $s['ai_default_agent'] ); ?>" class="regular-text" placeholder="UUID agent (opsional, kosongkan untuk default portal)" />
					<p class="description">Aktifkan dan simpan dulu, lalu klik "Refresh Agent" setelah koneksi tersambung.</p>
				</td>
			</tr>
			<tr>
				<th>Isi Otomatis</th>
				<td>
					<label><input type="checkbox" name="ics_settings[ai_auto_fill_title]" value="1" <?php checked( $s['ai_auto_fill_title'], 1 ); ?> /> Isi judul otomatis</label><br />
					<label><input type="checkbox" name="ics_settings[ai_auto_fill_excerpt]" value="1" <?php checked( $s['ai_auto_fill_excerpt'], 1 ); ?> /> Isi excerpt otomatis</label>
				</td>
			</tr>
		</table>

		<?php submit_button( 'Simpan Pengaturan' ); ?>
	</form>

	<hr />

	<h2 class="title">Versi &amp; Pembaruan</h2>
	<?php
	$update_transient = get_site_transient( 'update_plugins' );
	$has_update = $update_transient && isset( $update_transient->response[ ICS_PLUGIN_BASENAME ] );
	?>
	<table class="form-table" role="presentation">
		<tr>
			<th>Versi Terpasang</th>
			<td><strong><?php echo esc_html( ICS_VERSION ); ?></strong></td>
		</tr>
		<tr>
			<th>Status</th>
			<td>
				<?php if ( $has_update ) : ?>
					<span style="color:#d63638;font-weight:600;">Ada pembaruan tersedia!</span>
				<?php else : ?>
					<span style="color:#059669;font-weight:600;">Terbaru</span>
				<?php endif; ?>
			</td>
		</tr>
		<tr>
			<th></th>
			<td>
				<a href="<?php echo wp_nonce_url( admin_url( 'admin-post.php?action=ics_force_check_update' ), 'ics_force_check_update' ); ?>" class="button button-secondary">
					Cek Pembaruan
				</a>
				<?php if ( $has_update ) : ?>
					&nbsp;
					<a href="<?php echo wp_nonce_url( admin_url( 'admin-post.php?action=ics_update_plugin' ), 'ics_update_plugin' ); ?>" class="button button-primary">
						Update Sekarang
					</a>
				<?php endif; ?>
			</td>
		</tr>
	</table>
	<?php if ( isset( $_GET['ics_msg'] ) && in_array( $_GET['ics_msg'], array( 'update_available', 'up_to_date', 'update_success', 'update_fail' ), true ) ) : ?>
		<?php if ( 'update_available' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-warning"><p>Pembaruan ditemukan! Klik "Update Sekarang" untuk menginstal.</p></div>
		<?php else : ?>
			<div class="notice notice-success"><p>Plugin sudah versi terbaru.</p></div>
		<?php endif; ?>
		<?php if ( 'update_success' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-success"><p>Plugin berhasil diperbarui.</p></div>
		<?php elseif ( 'update_fail' === $_GET['ics_msg'] ) : ?>
			<div class="notice notice-error"><p>Pembaruan gagal: <?php echo esc_html( isset( $_GET['ics_err'] ) ? rawurldecode( wp_unslash( $_GET['ics_err'] ) ) : 'Kesalahan tidak diketahui.' ); ?></p></div>
		<?php endif; ?>
	<?php endif; ?>
</div>
