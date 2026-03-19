// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://robkisk.github.io',
	base: '/aidevkit.github.io',
	integrations: [
		starlight({
			title: 'AI Dev Kit',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/databricks-solutions/ai-dev-kit' },
			],
			sidebar: [
				{ label: 'Getting Started', autogenerate: { directory: 'getting-started' } },
			],
			lastUpdated: true,
		}),
	],
});
