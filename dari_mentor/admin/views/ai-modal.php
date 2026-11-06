<div id="ics-ai-modal" class="ics-modal-overlay" style="display:none;">
	<div class="ics-modal" role="dialog" aria-labelledby="ics-ai-title" aria-modal="true">
		<div class="ics-modal-header">
			<h2 id="ics-ai-title">Inova AI Writer</h2>
			<button type="button" class="ics-modal-close" onclick="icsAiClose()">&times;</button>
		</div>
		<div class="ics-modal-body">
			<div id="ics-ai-form">
				<div class="ics-field">
					<label for="ics-ai-title-input">Judul / Topik <span style="color:#dc2626">*</span></label>
					<input type="text" id="ics-ai-title-input" class="ics-input" placeholder="Tulis judul atau topik artikel..." />
				</div>
				<div class="ics-field-row">
					<div class="ics-field">
						<label for="ics-ai-agent">Agent</label>
						<select id="ics-ai-agent" class="ics-select"></select>
					</div>
					<div class="ics-field">
						<label for="ics-ai-tone">Tone</label>
						<select id="ics-ai-tone" class="ics-select">
							<option value="">Default</option>
							<option value="jernih, analitis, mudah dibaca">Jernih & analitis</option>
							<option value="formal, profesional">Formal</option>
							<option value="santai, mengalir">Santai</option>
							<option value="berwibawa, tegas">Tegas</option>
						</select>
					</div>
				</div>
				<div class="ics-field">
					<label for="ics-ai-keywords">Kata Kunci</label>
					<input type="text" id="ics-ai-keywords" class="ics-input" placeholder="pisahkan dengan koma" />
				</div>
				<div class="ics-field">
					<label for="ics-ai-angle">Angle / Sudut Pandang</label>
					<input type="text" id="ics-ai-angle" class="ics-input" placeholder="opsional" />
				</div>
				<div class="ics-field">
					<label for="ics-ai-instructions">Instruksi Tambahan</label>
					<textarea id="ics-ai-instructions" class="ics-textarea" rows="2" placeholder="instruksi khusus untuk AI..."></textarea>
				</div>
				<div class="ics-field">
					<label for="ics-ai-source-url">URL Sumber</label>
					<input type="url" id="ics-ai-source-url" class="ics-input" placeholder="https://..." />
				</div>
			</div>

			<div id="ics-ai-progress" style="display:none;">
				<div class="ics-spinner"></div>
				<p id="ics-ai-progress-text">Mengirim permintaan...</p>
				<p style="font-size:0.85em;color:#666;margin-top:0.5rem">Biasanya 30-60 detik. Jangan tutup halaman.</p>
			</div>

			<div id="ics-ai-error" style="display:none;" class="ics-error-box"></div>

			<div id="ics-ai-confirm" style="display:none;">
				<p>Artikel siap! Editor sudah terisi.</p>
				<p style="font-size:0.85em;color:#666">Artikel juga tersimpan sebagai draft di CMS.</p>
			</div>
		</div>
		<div class="ics-modal-footer">
			<span id="ics-ai-credits" class="ics-credits-info"></span>
			<button type="button" class="button button-secondary" onclick="icsAiClose()">Tutup</button>
			<button type="button" id="ics-ai-submit" class="button button-primary" onclick="icsAiGenerate()">Tulis dengan AI</button>
		</div>
	</div>
</div>
