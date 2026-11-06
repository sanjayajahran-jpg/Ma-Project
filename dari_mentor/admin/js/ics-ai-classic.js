/**
 * Classic Editor integration.
 */
(function($) {
	'use strict';

	$(document).ready(function() {
		$('#ics-ai-button').on('click', function(e) {
			e.preventDefault();
			window.icsAiOpen();
		});
	});

	window.icsAiFillClassic = function(article) {
		var contentHtml = article.contentHtml || article.content || '';
		var title = icsAiData.autoFillTitle ? (article.title || '') : '';

		// Check for existing content
		var existing = '';
		var editor = (typeof tinymce !== 'undefined') ? tinymce.get('content') : null;
		if (editor && !editor.isHidden()) {
			existing = editor.getContent();
		} else {
			existing = $('#content').val() || '';
		}

		if (existing && existing.trim()) {
			if (!confirm('Editor sudah ada konten. Ganti seluruhnya?')) {
				return;
			}
		}

		// Fill title
		if (title) {
			$('#title').val(title).trigger('input').trigger('blur');
		}

		// Fill excerpt
		if (icsAiData.autoFillExcerpt && article.excerpt) {
			$('#excerpt').val(article.excerpt);
		}

		// Fill content — both TinyMCE and textarea for safety
		if (editor && !editor.isHidden()) {
			editor.setContent(contentHtml);
			editor.undoManager.add();
			editor.setDirty(true);
			editor.fire('change');
		}
		$('#content').val(contentHtml).trigger('change');
	};
})(jQuery);
