import {defineCollection} from 'astro:content';
import {glob} from 'astro/loaders';
import {z} from 'astro/zod';
const schema=z.object({title:z.string(),description:z.string(),order:z.number(),stage:z.number().int().min(1).max(10).default(1),minutes:z.number().positive(),revision:z.number().int().positive().default(2),introduces:z.array(z.string()).default([]),requires:z.array(z.string()).default([]),terms:z.array(z.string()).default([]),sources:z.array(z.string()).min(1),sessions:z.array(z.string()).default([]),prerequisites:z.array(z.string()).default([]),question:z.string(),answer:z.string(),bridge:z.string(),status:z.enum(['preview','reviewed']).default('preview'),environment:z.string().optional(),verification:z.string().default('内容审校；待真实试读'),project:z.string().optional()});
export const collections={
 chapters:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/chapters'}),schema}),
 projects:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/projects'}),schema}),
 code:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/code'}),schema}),
 advanced:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/advanced'}),schema})
};
