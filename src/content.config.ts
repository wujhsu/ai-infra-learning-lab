import {defineCollection} from 'astro:content';
import {glob} from 'astro/loaders';
import {z} from 'astro/zod';
const schema=z.object({title:z.string(),description:z.string(),order:z.number(),module:z.number().min(0).max(7).default(0),minutes:z.number().default(25),prerequisites:z.array(z.string()).default([]),terms:z.array(z.string()).default([]),sources:z.array(z.string()).min(1),sessions:z.array(z.string()).default([]),lab:z.string().optional(),question:z.string(),answer:z.string(),verified:z.string().default('文档核验；硬件实验未在本机运行')});
export const collections={
 lessons:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/lessons'}),schema}),
 topics:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/topics'}),schema}),
 labs:defineCollection({loader:glob({pattern:'**/*.mdx',base:'./src/content/labs'}),schema}),
};
