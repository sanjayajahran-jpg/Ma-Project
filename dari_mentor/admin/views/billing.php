<?php if ( ! defined( 'ABSPATH' ) ) exit; ?>
<div class="wrap">
	<h1>Top Up Saldo AI</h1>
	<p class="description">Isi saldo kredit AI langsung dari WordPress. Setelah pembayaran berhasil, saldo akan diproses otomatis oleh CMS.</p>

	<?php if ( isset( $_GET['ics_msg'] ) && 'topup_fail' === $_GET['ics_msg'] ) : ?>
		<div class="notice notice-error"><p><?php echo esc_html( rawurldecode( $_GET['ics_err'] ?? 'Top up gagal.' ) ); ?></p></div>
	<?php elseif ( isset( $_GET['ics_msg'] ) && 'topup_created' === $_GET['ics_msg'] ) : ?>
		<div class="notice notice-success"><p>Transaksi top up dibuat. Silakan lanjutkan pembayaran dari halaman Duitku.</p></div>
	<?php endif; ?>

	<div style="max-width:760px;margin-top:20px;background:#fff;border:1px solid #dcdcde;padding:24px;">
		<h2 style="margin-top:0;">Buat Top Up</h2>
		<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<input type="hidden" name="action" value="ics_create_topup" />
			<?php wp_nonce_field( 'ics_create_topup' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th><label for="ics_topup_amount">Nominal</label></th>
					<td>
						<select id="ics_topup_amount" name="amount" required>
							<option value="50000">Rp 50.000</option>
							<option value="100000" selected>Rp 100.000</option>
							<option value="200000">Rp 200.000</option>
							<option value="500000">Rp 500.000</option>
							<option value="1000000">Rp 1.000.000</option>
						</select>
						<p class="description">Minimum top up Rp 10.000.</p>
					</td>
				</tr>
				<tr>
					<th><label for="ics_topup_method">Metode pembayaran</label></th>
					<td>
						<?php if ( $billing_error ) : ?>
							<p style="color:#b32d2e;"><?php echo esc_html( $billing_error ); ?></p>
						<?php elseif ( empty( $methods ) ) : ?>
							<p>Metode pembayaran belum tersedia.</p>
						<?php else : ?>
							<select id="ics_topup_method" name="payment_method" required>
								<?php foreach ( $methods as $method ) : ?>
									<option value="<?php echo esc_attr( $method['paymentMethod'] ?? $method['payment_method'] ?? '' ); ?>"><?php echo esc_html( $method['paymentName'] ?? $method['payment_name'] ?? '' ); ?><?php if ( ! empty( $method['totalFee'] ?? $method['total_fee'] ) ) : ?> — fee <?php echo esc_html( $method['totalFee'] ?? $method['total_fee'] ); ?><?php endif; ?></option>
								<?php endforeach; ?>
							</select>
						<?php endif; ?>
					</td>
				</tr>
			</table>
			<?php submit_button( 'Lanjutkan Pembayaran', 'primary', 'submit', true, empty( $methods ) ? array( 'disabled' => 'disabled' ) : array() ); ?>
		</form>
	</div>

	<div style="max-width:760px;margin-top:20px;background:#f6f7f7;border-left:4px solid #2271b1;padding:16px 20px;">
		<h2 style="margin-top:0;font-size:16px;">Riwayat transaksi dan invoice</h2>
		<p>Untuk melihat seluruh record transaksi atau mengunduh invoice, silakan login ke <?php echo esc_html( $provider['label'] ); ?>.</p>
		<a class="button button-secondary" href="<?php echo esc_url( $provider['url'] ); ?>" target="_blank" rel="noopener">Buka Billing CMS ↗</a>
	</div>
</div>
