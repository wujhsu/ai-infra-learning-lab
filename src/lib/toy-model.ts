import model from '../data/toy-model.json';
export {model};
export function dot(a:number[],b:number[]){if(a.length!==b.length)throw new Error('向量长度不同');return a.reduce((s,x,i)=>s+x*b[i],0);}
export function project(x:number[],w:number[][]){if(x.length!==w.length)throw new Error('矩阵维度不匹配');return w[0].map((_,j)=>x.reduce((s,v,i)=>s+v*w[i][j],0));}
export function softmax(scores:number[]){if(!scores.length)throw new Error('至少需要一个候选');const m=Math.max(...scores);const e=scores.map(x=>Math.exp(x-m));const sum=e.reduce((a,b)=>a+b,0);return e.map(x=>x/sum);}
export function attend(q:number[],keys:number[][],values:number[][]){if(!keys.length||keys.length!==values.length)throw new Error('K/V 长度必须相同且非空');const scores=keys.map(k=>dot(q,k)/Math.sqrt(q.length));const weights=softmax(scores);const output=values[0].map((_,j)=>values.reduce((s,v,i)=>s+weights[i]*v[j],0));return {scores,weights,output};}
export function projections(ids:number[]){const x=ids.map(id=>{if(!model.embeddings[id])throw new Error('未知 token ID');return model.embeddings[id];});return {q:x.map(v=>project(v,model.wq)),k:x.map(v=>project(v,model.wk)),v:x.map(v=>project(v,model.wv))};}
export function fullAttention(ids:number[]){const {q,k,v}=projections(ids);return q.map((row,i)=>attend(row,k.slice(0,i+1),v.slice(0,i+1)));}
export function cachedStep(id:number,cache:{k:number[][];v:number[][]}){const {q,k,v}=projections([id]);const next={k:[...cache.k,...k],v:[...cache.v,...v]};return {...attend(q[0],next.k,next.v),cache:next};}
