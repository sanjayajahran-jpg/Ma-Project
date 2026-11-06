(function($) {
	'use strict';

	$(document).ready(function() {

		// Save post meta flag when post is edited locally
		if (typeof wp !== 'undefined' && wp.data && wp.data.subscribe) {
			var wasDirty = false;
			wp.data.subscribe(function() {
				var isDirty = wp.data.select('core/editor') && wp.data.select('core/editor').isEditedPostDirty();
				if (isDirty && !wasDirty) {
					$.post(ajaxurl, {
						action: 'ics_mark_edited',
						post_id: $('#post_ID').val() || 0,
						nonce: (window.ics_nonce || '')
					});
				}
				wasDirty = isDirty;
			});
		}

		// Classic editor: detect changes
		$(document).on('input change', '#title, #content, #excerpt', function() {
			var postId = $('#post_ID').val() || 0;
			if (postId && !$(this).data('ics-marked')) {
				$(this).data('ics-marked', true);
				$.post(ajaxurl, {
					action: 'ics_mark_edited',
					post_id: postId,
					nonce: (window.ics_nonce || '')
				});
			}
		});

		// Auto-prune logs on status page visit
		if ($('#ics-status-page').length) {
			$.post(ajaxurl, {
				action: 'ics_prune_logs',
				nonce: (window.ics_nonce || '')
			});
		}
	});
})(jQuery);
