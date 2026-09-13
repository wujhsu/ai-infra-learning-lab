import{readFile,writeFile}from'node:fs/promises';
const sources=JSON.parse(await readFile('src/data/sources.json','utf8'));const results=[];
for(let i=0;i<sources.length;i+=5){await Promise.allSettled(sources.slice(i,i+5).map(async s=>{try{const r=await fetch(s.url,{signal:AbortSignal.timeout(20000)});const html=await r.text();results.push({id:s.id,url:s.url,resolved:r.url,status:r.status,title:html.match(/<title[^>]*>(.*?)<\/title>/s)?.[1]?.slice(0,180)||'',checked:new Date().toISOString()});if(!r.ok)console.log(s.id,r.status,s.url);}catch(e){results.push({id:s.id,url:s.url,status:0,error:e.message});console.log(s.id,e.message);}}));}
await writeFile('src/data/source-checks.json',JSON.stringify(results,null,2));console.log('Checked',results.length,'sources');
