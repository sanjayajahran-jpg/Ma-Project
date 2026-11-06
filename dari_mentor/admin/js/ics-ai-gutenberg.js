/**
 * Gutenberg (block editor) integration.
 */
(function() {
	'use strict';

	if (typeof wp === 'undefined' || !wp.plugins || !wp.element) {
		return;
	}

	var registerPlugin = wp.plugins.registerPlugin;
	var el = wp.element.createElement;
	var Fragment = wp.element.Fragment;
	var PluginSidebar = wp.editPost.PluginSidebar;
	var Button = wp.components.Button;
	var dispatch = wp.data.dispatch;

	registerPlugin('insight-cms-ai', {
		render: function() {
			return el(Fragment, {},
				el(PluginSidebar, {
					name: 'ics-ai-panel',
					title: 'Inova AI',
					icon: 'star-filled',
				},
					el('div', { style: { padding: '16px' } },
						el(Button, {
							isPrimary: true,
							onClick: function() {
								window.icsAiOpen();
							},
						}, 'Inova AI Writer')
					)
				)
			);
		},
	});

	window.icsAiFillGutenberg = function(article) {
		var contentHtml = article.contentHtml || article.content || '';

		if (icsAiData.autoFillTitle && article.title) {
			dispatch('core/editor').editPost({ title: article.title });
		}
		if (icsAiData.autoFillExcerpt && article.excerpt) {
			dispatch('core/editor').editPost({ excerpt: article.excerpt });
		}

		// Convert HTML to blocks
		if (wp.blocks && wp.blocks.rawHandler) {
			var blocks = wp.blocks.rawHandler({ HTML: contentHtml });
			if (blocks && blocks.length) {
				dispatch('core/block-editor').resetBlocks(blocks);
			}
		}
	};
})();
