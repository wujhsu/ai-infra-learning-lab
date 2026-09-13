export type RecordEntry={read:boolean;understood:boolean;lab:boolean;bookmark:boolean;review:boolean;note:string;anchor:string;updated:string;revision:number};
export type Store={version:2;records:Record<string,RecordEntry>;last:string;settings:{theme:string;size:number;line:number}};
export const key='ai-infra-library:v2';
export const emptyEntry=():RecordEntry=>({read:false,understood:false,lab:false,bookmark:false,review:false,note:'',anchor:'',revision:2,updated:new Date().toISOString()});
export const emptyStore=():Store=>({version:2,records:{},last:'',settings:{theme:'light',size:18,line:1.9}});
export function validateStore(raw:unknown):Store{
 if(!raw||typeof raw!=='object')throw new Error('文件不是学习记录');
 const s=raw as Store;if(s.version!==2||!s.records||typeof s.records!=='object'||Array.isArray(s.records))throw new Error('不支持的记录版本');
 const safe=emptyStore();
 for(const [id,r] of Object.entries(s.records)){
  if(!/^(read|projects|code|advanced|terms)\/[a-z0-9-]+$/.test(id)||!r||typeof r!=='object')throw new Error('记录 ID 不合法');
  if(['read','understood','lab','bookmark','review'].some(k=>typeof r[k as keyof RecordEntry]!=='boolean')||typeof r.note!=='string'||r.note.length>100000||typeof r.anchor!=='string'||!Number.isFinite(Date.parse(r.updated)))throw new Error('记录字段不完整');
  safe.records[id]={read:r.read,understood:r.understood,lab:r.lab,bookmark:r.bookmark,review:r.review,note:r.note,anchor:r.anchor,updated:r.updated,revision:Number.isInteger(r.revision)&&r.revision>0?r.revision:2};
 }
 safe.last=typeof s.last==='string'&&s.last in safe.records?s.last:'';
 if(s.settings){safe.settings={theme:s.settings.theme==='dark'?'dark':'light',size:[17,18,20,22].includes(s.settings.size)?s.settings.size:18,line:[1.7,1.9,2.1].includes(s.settings.line)?s.settings.line:1.9};}
 return safe;
}
export function mergeStores(current:Store,incoming:Store,mode:'newer'|'keep'|'replace'):Store{
 const records={...current.records};for(const [id,r] of Object.entries(incoming.records)){if(!records[id]||mode==='replace'||(mode==='newer'&&Date.parse(r.updated)>Date.parse(records[id].updated)))records[id]=r;}
 return{...current,records,last:current.last||incoming.last};
}
export function readStore():Store{try{const raw=localStorage.getItem(key);return raw?validateStore(JSON.parse(raw)):emptyStore();}catch{return emptyStore();}}
export function saveStore(s:Store){try{localStorage.setItem(key,JSON.stringify(s));window.dispatchEvent(new Event('learning-change'));return true;}catch{return false;}}
