import {defineConfig} from 'astro/config';
import {unified} from '@astrojs/markdown-remark';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
export default defineConfig({
 site:'https://wujhsu.github.io', base:'/ai-infra-learning-lab/', trailingSlash:'always',
 integrations:[mdx(),react()],
 markdown:{processor:unified({remarkPlugins:[remarkMath],rehypePlugins:[rehypeKatex]}),shikiConfig:{theme:'github-dark'}},
});
