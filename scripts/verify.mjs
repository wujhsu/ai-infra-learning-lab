import {readFileSync,readdirSync,existsSync,statSync} from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const read=p=>readFileSync(p,'utf8');
const json=p=>JSON.parse(read(p));
const walk=dir=>readdirSync(dir).flatMap(n=>{const p=path.join(dir,n);return statSync(p).isDirectory()?walk(p):[p]});
const sources=json('src/data/sources.json'),terms=json('src/data/glossary.json'),slides=json('src/data/slides.json'),sessions=json('src/data/sessions.json');
assert.equal(slides.length,214);assert.equal(sessions.length,12);
for(const list of [sources,terms,slides,sessions])assert.equal(new Set(list.map(x=>x.id)).size,list.length,'Duplicate stable ID');
for(const s of slides)if(s.selected){assert(existsSync('public/'+s.image));assert(existsSync('public/'+s.highres));}
const collections=['chapters','projects','code','advanced'];
const reading=json('src/data/reading.json'),concepts=json('src/data/concepts.json');
const counts={chapters:reading.length,projects:5,code:6,advanced:7};
assert.equal(new Set(reading.map(x=>x.id)).size,reading.length);
assert.equal(new Set(concepts.map(x=>x.id)).size,concepts.length);
for(const old of ['learn','labs','topics','archive','legacy'])assert(!existsSync('dist/'+old),'Old route remains: '+old);
for(const old of ['lessons','topics','labs'])assert(!existsSync('src/content/'+old),'Old content remains: '+old);
let chapters=0;
for(const col of collections){const files=walk('src/content/'+col).filter(p=>p.endsWith('.mdx'));assert.equal(files.length,counts[col]);
 for(const file of files){const content=read(file);chapters++;const fm=content.split('---')[1];
  const field=name=>JSON.parse(fm.match(new RegExp('^'+name+': (.+)$','m'))?.[1]||'[]');
  for(const id of field('sources'))assert(sources.some(s=>s.id===id),`${file}: missing source ${id}`);
  for(const id of field('terms'))assert(terms.some(s=>s.id===id),`${file}: missing term ${id}`);
  for(const id of field('sessions'))assert(sessions.some(s=>s.id===id),`${file}: missing session ${id}`);
  for(const id of field('prerequisites'))assert(existsSync(`src/content/chapters/${id}.mdx`),`${file}: missing prerequisite`);
  for(const m of content.matchAll(/<Slide id="([^"]+)"/g))assert(slides.some(s=>s.id===m[1]&&s.selected),`${file}: missing slide ${m[1]}`);
  for(const m of content.matchAll(/<Term id="([^"]+)"/g))assert(terms.some(t=>t.id===m[1]),`${file}: missing inline term`);
  for(const id of field('introduces'))assert(concepts.some(x=>x.id===id&&x.firstChapter===path.basename(file,'.mdx')),`${file}: inconsistent concept introduction ${id}`);
  for(const id of field('requires')){const c=concepts.find(x=>x.id===id);assert(c,`${file}: missing concept ${id}`);if(col==='chapters')assert(reading.find(x=>x.id===c.firstChapter).order<reading.find(x=>x.id===path.basename(file,'.mdx')).order,`${file}: forward prerequisite ${id}`);}
  for(const m of content.matchAll(/<Demo type="([^"]+)"/g))assert(['latency','kv','batch','cache','overlap','dra'].includes(m[1]),'Unknown demo');
  assert(!content.includes('<Demo kind='),'Incorrect demo prop');
  assert(content.includes('question:')&&content.includes('answer:'),`${file}: missing self check`);
 }
}
const base='/ai-infra-learning-lab/';let links=0;
const htmls=walk('dist').filter(p=>p.endsWith('.html'));
const idCache=new Map();
for(const file of htmls){const html=read(file);
 assert(!/feishu\.cn\/minutes|larksuite\.com\/minutes|minute\.json|\/Users\/angus|open_id|user_access_token/.test(html),`Private source leak: ${file}`);
 for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){
  const url=match[1];if(!url.startsWith('/')||url.startsWith('//'))continue;
  assert(url.startsWith(base),`Incorrect Pages base ${url} in ${file}`);
  const [pathname,hash]=url.slice(base.length).split('#');
  let target=path.join('dist',decodeURIComponent(pathname.split('?')[0]));
  if(url.split('#')[0].endsWith('/'))target=path.join(target,'index.html');
  assert(existsSync(target),`Broken local link ${url} in ${file}`);links++;
  if(hash&&target.endsWith('.html')){let ids=idCache.get(target);if(!ids){ids=new Set([...read(target).matchAll(/id="([^"]+)"/g)].map(m=>m[1]));idCache.set(target,ids);}assert(ids.has(decodeURIComponent(hash)),`Missing anchor ${url}`);}
 }
}
assert(existsSync('dist/pagefind/pagefind.js'));assert(existsSync('dist/downloads/labs.zip'));
console.log(`Verified ${chapters} learning entries, ${slides.length} slide pages, ${htmls.length} HTML pages and ${links} internal links/assets. No private-minute paths in published HTML.`);
