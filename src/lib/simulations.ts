export function latency(queue:number,prefill:number,network:number,tpot:number,tokens:number){
 if([queue,prefill,network,tpot].some(n=>!Number.isFinite(n)||n<0)||!Number.isInteger(tokens)||tokens<1)throw new Error('Invalid latency inputs');
 return {ttft:queue+prefill+network,total:queue+prefill+network+tpot*(tokens-1)};
}
export function kvBytes(layers:number,heads:number,dim:number,tokens:number,batch:number,bytes:number){
 const values=[layers,heads,dim,tokens,batch,bytes];if(values.some(n=>!Number.isFinite(n)||n<=0))throw new Error('All dimensions must be positive');
 return 2*layers*heads*dim*tokens*batch*bytes;
}
export function overlap(tiles:number,transfer:number,compute:number){
 if(!Number.isInteger(tiles)||tiles<1||[transfer,compute].some(n=>!Number.isFinite(n)||n<0))throw new Error('Invalid pipeline');
 return {serial:tiles*(transfer+compute),pipelined:transfer+compute+(tiles-1)*Math.max(transfer,compute)};
}
export type BatchRequest={id:string;arrival:number;tokens:number};
export const requests:BatchRequest[]=[{id:'A',arrival:0,tokens:5},{id:'B',arrival:0,tokens:2},{id:'C',arrival:1,tokens:3},{id:'D',arrival:3,tokens:2}];
export function batching(step:number,capacity:number,continuous:boolean){
 if(!Number.isInteger(step)||step<0||!Number.isInteger(capacity)||capacity<1)throw new Error('Invalid batch configuration');
 const remaining=new Map(requests.map(r=>[r.id,r.tokens]));let active:string[]=[];const rows:{time:number,active:string[],waiting:string[],finished:string[]}[]=[];
 for(let time=0;time<=step;time++){
  if(continuous||active.length===0){for(const r of requests){if(r.arrival<=time&&remaining.get(r.id)!>0&&!active.includes(r.id)&&active.length<capacity)active.push(r.id);}}
  const working=active.filter(id=>remaining.get(id)!>0);
  for(const id of working)remaining.set(id,remaining.get(id)!-1);
  rows.push({time,active:working,waiting:requests.filter(r=>r.arrival<=time&&remaining.get(r.id)!>0&&!active.includes(r.id)).map(r=>r.id),finished:requests.filter(r=>remaining.get(r.id)===0).map(r=>r.id)});
  if(continuous)active=active.filter(id=>remaining.get(id)!>0);else if(active.every(id=>remaining.get(id)===0))active=[];
 }return rows;
}
export function cacheBenefit(sizeGB:number,bandwidth:number,recomputeMs:number,overheadMs:number){
 if([sizeGB,bandwidth,recomputeMs,overheadMs].some(n=>!Number.isFinite(n))||sizeGB<0||bandwidth<=0||recomputeMs<0||overheadMs<0)throw new Error('Invalid cache inputs');
 const loadMs=sizeGB/bandwidth*1000+overheadMs;return{loadMs,savingMs:recomputeMs-loadMs,worthwhile:loadMs<recomputeMs};
}
export const cacheTrace=['root','middle','tail','other','root','middle','tail','END','other'];
export function cachePolicy(step:number,policy:'lru'|'prefix'|'session'){
 if(!Number.isInteger(step)||step<0||step>=cacheTrace.length||!['lru','prefix','session'].includes(policy))throw new Error('Invalid cache trace');
 let cache:string[]=[];let hits=0,misses=0;const capacity=3;
 for(const key of cacheTrace.slice(0,step+1)){
  if(key==='END'){if(policy==='session')cache=cache.filter(k=>!['root','middle','tail'].includes(k));continue;}
  if(cache.includes(key)){hits++;cache=cache.filter(k=>k!==key);cache.push(key);continue;}
  misses++;
  if(cache.length>=capacity){const tail=cache.indexOf('tail');if(policy!=='lru'&&tail>=0)cache.splice(tail,1);else cache.shift();}
  cache.push(key);
 }return{cache,hits,misses};
}
export const devices=[{id:'GPU-0',memory:80,numa:0,healthy:true},{id:'GPU-1',memory:24,numa:1,healthy:true},{id:'GPU-2',memory:80,numa:1,healthy:false}];
export function selectDevices(memory:number,sameNuma:boolean){if(!Number.isFinite(memory)||memory<=0)throw new Error('Invalid device capacity');return devices.filter(d=>d.healthy&&d.memory>=memory&&(!sameNuma||d.numa===0));}

export function gradientUpdate(rate:number){if(!Number.isFinite(rate)||rate<0)throw new Error("Invalid rate");const next=2-rate*(-8);return{next,loss:(next*2-6)**2};}
