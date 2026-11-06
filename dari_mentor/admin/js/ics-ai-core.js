/**
 * ICS AI Core — shared logic for Classic + Gutenberg editors.
 */
(function($) {
	'use strict';

	window.icsAiData = (typeof icsAi !== 'undefined') ? icsAi : { enabled: false, agents: [] };
	window.icsAiState = {
		polling: false,
		articleId: null,
		jobId: null,
	};

	window.icsAiOpen = function() {
		// Reset form
		$('#ics-ai-title-input').val($('#title').val() || '');
		$('#ics-ai-angle, #ics-ai-keywords, #ics-ai-instructions, #ics-ai-source-url').val('');
		$('#ics-ai-error').hide();
		$('#ics-ai-progress').hide();
		$('#ics-ai-confirm').hide();
		$('#ics-ai-form').show();
		$('#ics-ai-submit').prop('disabled', false);

		// Populate agents
		var $agentSelect = $('#ics-ai-agent');
		$agentSelect.empty();
		if (icsAiData.agents && icsAiData.agents.length) {
			icsAiData.agents.forEach(function(a) {
				$agentSelect.append('<option value="' + a.id + '"' + (a.isDefault || a.id === icsAiData.defaultAgent ? ' selected' : '') + '>' + a.name + ' (' + a.model + ')</option>');
			});
		}

		// Show credits
		if (icsAiData.credits !== null && icsAiData.credits !== undefined) {
			$('#ics-ai-credits').text('Saldo: Rp ' + icsAiData.credits.toLocaleString('id-ID'));
		}

		$('#ics-ai-modal').show();
	};

	window.icsAiClose = function() {
		if (icsAiState.polling) {
			if (!confirm('AI masih bekerja. Yakin ingin menutup?')) return;
			icsAiState.polling = false;
		}
		$('#ics-ai-modal').hide();
	};

	window.icsAiGenerate = function() {
		var title = $('#ics-ai-title-input').val().trim();
		if (!title) {
			$('#ics-ai-error').text('Judul wajib diisi.').show();
			return;
		}

		$('#ics-ai-error').hide();
		$('#ics-ai-form').hide();
		$('#ics-ai-submit').prop('disabled', true);
		$('#ics-ai-progress').show();
		$('#ics-ai-progress-text').text('Mengirim permintaan...');

		$.post(icsAiData.ajaxUrl, {
			action: 'ics_ai_generate',
			nonce: icsAiData.nonce,
			title: title,
			angle: $('#ics-ai-angle').val(),
			keywords: $('#ics-ai-keywords').val(),
			tone: $('#ics-ai-tone').val(),
			instructions: $('#ics-ai-instructions').val(),
			source_url: $('#ics-ai-source-url').val(),
			agent_id: $('#ics-ai-agent').val(),
		}).done(function(resp) {
			if (resp.success) {
				icsAiState.jobId = resp.data.jobId;
				icsAiState.articleId = resp.data.articleId;
				$('#ics-ai-progress-text').text('AI sedang menulis...');
				icsAiState.polling = true;
				icsAiPoll(0);
			} else {
				icsAiShowError(resp.data?.message || 'Gagal membuat job AI.');
			}
		}).fail(function(xhr) {
			var msg = xhr.responseJSON?.data?.message || 'Kesalahan koneksi ke server CMS.';
			icsAiShowError(msg);
		});
	};

	function icsAiPoll(attempt) {
		if (!icsAiState.polling) return;
		if (attempt > 60) { // ~3 min at 3s interval
			icsAiShowError('Waktu tunggu habis. Artikel mungkin tetap jadi di CMS. Article ID: ' + icsAiState.articleId);
			return;
		}

		$.post(icsAiData.ajaxUrl, {
			action: 'ics_ai_poll',
			nonce: icsAiData.nonce,
			job_id: icsAiState.jobId,
		}).done(function(resp) {
			if (!resp.success) {
				icsAiShowError(resp.data?.message || 'Gagal mengecek status.');
				return;
			}

			var status = resp.data.status;
			if (status === 'succeeded') {
				$('#ics-ai-progress-text').text('Mengambil hasil...');
				icsAiFetchArticle();
			} else if (status === 'failed') {
				icsAiShowError(resp.data.errorMessage || 'AI gagal membuat artikel.');
			} else {
				// still queued/running
				setTimeout(function() { icsAiPoll(attempt + 1); }, 3000);
			}
		}).fail(function() {
			setTimeout(function() { icsAiPoll(attempt + 1); }, 3000);
		});
	}

	function icsAiFetchArticle() {
		$.post(icsAiData.ajaxUrl, {
			action: 'ics_ai_get_article',
			nonce: icsAiData.nonce,
			article_id: icsAiState.articleId,
		}).done(function(resp) {
			if (resp.success) {
				var article = resp.data;
				icsAiFillEditor(article);
				$('#ics-ai-progress').hide();
				$('#ics-ai-confirm').show();
				icsAiState.polling = false;
			} else {
				icsAiShowError('Gagal mengambil artikel hasil.');
			}
		}).fail(function() {
			icsAiShowError('Gagal mengambil artikel hasil.');
		});
	}

	window.icsAiFillEditor = function(article) {
		// Filled by editor-specific JS (classic or gutenberg)
		if (typeof window.icsAiFillClassic === 'function' && !icsAiData.isBlockEditor) {
			window.icsAiFillClassic(article);
		} else if (typeof window.icsAiFillGutenberg === 'function') {
			window.icsAiFillGutenberg(article);
		}
	};

	function icsAiShowError(msg) {
		icsAiState.polling = false;
		$('#ics-ai-progress').hide();
		$('#ics-ai-form').show();
		$('#ics-ai-submit').prop('disabled', false);
		$('#ics-ai-error').text(msg).show();
	}

	// Close on overlay click + Esc
	$(document).ready(function() {
		$('#ics-ai-modal').on('click', function(e) {
			if (e.target === this) icsAiClose();
		});
		$(document).on('keydown', function(e) {
			if (e.keyCode === 27 && $('#ics-ai-modal').is(':visible')) {
				icsAiClose();
			}
		});
	});
})(jQuery);
