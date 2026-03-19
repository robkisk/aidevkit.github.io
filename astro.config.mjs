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
			logo: {
				src: './src/assets/Databricks_Logo.png',
			},
			components: {
				Hero: './src/components/Hero.astro',
			},
			customCss: ['./src/styles/databricks.css'],
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/databricks-solutions/ai-dev-kit' },
			],
			sidebar: [
				{ label: 'Getting Started', autogenerate: { directory: 'getting-started' } },
				{
					label: 'Skills',
					items: [
						{ label: 'Data Engineering', autogenerate: { directory: 'skills/data-engineering' } },
						{ label: 'SQL & Analytics', autogenerate: { directory: 'skills/sql-analytics' } },
						{ label: 'AI & ML', autogenerate: { directory: 'skills/ai-ml' } },
						{ label: 'Apps & Databases', autogenerate: { directory: 'skills/apps-databases' } },
						{ label: 'Governance & Catalog', autogenerate: { directory: 'skills/governance-catalog' } },
						{ label: 'DevOps & Config', autogenerate: { directory: 'skills/devops-config' } },
					],
				},
				{ label: 'MCP Tools', autogenerate: { directory: 'mcp-tools' } },
				{ label: 'Guides', autogenerate: { directory: 'guides' } },
				{ label: 'Prompt Library', autogenerate: { directory: 'prompt-library' } },
				{ label: 'Reference', autogenerate: { directory: 'reference' } },
			],
			lastUpdated: true,
		}),
	],
});
