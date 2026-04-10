// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://robkisk.github.io',
	base: '/aidevkit.github.io',
	integrations: [
		starlight({
			title: 'Dev Kit',
			head: [
				{ tag: 'link', attrs: { rel: 'preload', href: '/aidevkit.github.io/fonts/DMSans-Regular.woff2', as: 'font', type: 'font/woff2', crossorigin: '' } },
				{ tag: 'link', attrs: { rel: 'preload', href: '/aidevkit.github.io/fonts/DMSans-Medium.woff2', as: 'font', type: 'font/woff2', crossorigin: '' } },
				{ tag: 'link', attrs: { rel: 'preload', href: '/aidevkit.github.io/fonts/DMSans-Bold.woff2', as: 'font', type: 'font/woff2', crossorigin: '' } },
				{ tag: 'link', attrs: { rel: 'preload', href: '/aidevkit.github.io/fonts/JetBrainsMono-Regular.woff2', as: 'font', type: 'font/woff2', crossorigin: '' } },
			],
			expressiveCode: {
				themes: ['catppuccin-mocha', 'catppuccin-latte'],
			},
			logo: {
				src: './src/assets/header-logo.svg',
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
						{
							label: 'Data Engineering',
							items: [
								{ label: 'Spark Declarative Pipelines', autogenerate: { directory: 'skills/data-engineering/spark-declarative-pipelines' } },
								{ label: 'Custom Spark Data Sources', autogenerate: { directory: 'skills/data-engineering/custom-spark-data-sources' } },
								{ label: 'Spark Structured Streaming', autogenerate: { directory: 'skills/data-engineering/spark-structured-streaming' } },
								{ label: 'Zerobus Ingest', autogenerate: { directory: 'skills/data-engineering/zerobus-ingest' } },
							],
						},
						{
							label: 'SQL & Analytics',
							items: [
								{ label: 'AI Functions', autogenerate: { directory: 'skills/sql-analytics/ai-functions' } },
								{ label: 'Databricks SQL', autogenerate: { directory: 'skills/sql-analytics/databricks-sql' } },
								{ label: 'Genie Spaces', autogenerate: { directory: 'skills/sql-analytics/genie-spaces' } },
								{ label: 'Metric Views', autogenerate: { directory: 'skills/sql-analytics/metric-views' } },
								{ label: 'AI/BI Dashboards', autogenerate: { directory: 'skills/sql-analytics/aibi-dashboards' } },
							],
						},
						{
							label: 'AI & ML',
							items: [
								{ label: 'Vector Search', autogenerate: { directory: 'skills/ai-ml/vector-search' } },
								{ label: 'Agent Bricks', autogenerate: { directory: 'skills/ai-ml/agent-bricks' } },
								{ label: 'MLflow Evaluation', autogenerate: { directory: 'skills/ai-ml/mlflow-evaluation' } },
								{ label: 'Model Serving', autogenerate: { directory: 'skills/ai-ml/model-serving' } },
								{ label: 'Synthetic Data', autogenerate: { directory: 'skills/ai-ml/synthetic-data' } },
								{ label: 'Unstructured PDF Generation', autogenerate: { directory: 'skills/ai-ml/unstructured-pdf-generation' } },
							],
						},
						{
							label: 'Apps & Databases',
							items: [
								{ label: 'Databricks Apps (Python)', autogenerate: { directory: 'skills/apps-databases/databricks-apps-python' } },
								{ label: 'Databricks Apps (AppKit)', autogenerate: { directory: 'skills/apps-databases/databricks-apps-appkit' } },
								{ label: 'Lakebase Autoscaling', autogenerate: { directory: 'skills/apps-databases/lakebase-autoscale' } },
								{ label: 'Lakebase Provisioned', autogenerate: { directory: 'skills/apps-databases/lakebase-provisioned' } },
							],
						},
						{
							label: 'Governance & Catalog',
							items: [
								{ label: 'Iceberg Tables', autogenerate: { directory: 'skills/governance-catalog/iceberg-tables' } },
								{ label: 'Unity Catalog', autogenerate: { directory: 'skills/governance-catalog/unity-catalog' } },
							],
						},
						{
							label: 'DevOps & Config',
							items: [
								{ label: 'Asset Bundles', autogenerate: { directory: 'skills/devops-config/asset-bundles' } },
								{ label: 'Jobs Orchestration', autogenerate: { directory: 'skills/devops-config/jobs-orchestration' } },
								{ label: 'Workspace Config', autogenerate: { directory: 'skills/devops-config/workspace-config' } },
								{ slug: 'skills/devops-config/python-sdk' },
								{ label: 'Databricks Docs', autogenerate: { directory: 'skills/devops-config/databricks-docs' } },
								{ label: 'Execution & Compute', autogenerate: { directory: 'skills/devops-config/execution-compute' } },
							],
						},
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
