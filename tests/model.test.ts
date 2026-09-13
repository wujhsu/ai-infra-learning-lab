import test from 'node:test';
import assert from 'node:assert/strict';
import {model,fullAttention,cachedStep,softmax} from '../src/lib/toy-model';
import {gradientUpdate,cachePolicy,selectDevices} from '../src/lib/simulations';
test('causal attention and cached steps agree for every prefix and preserve old cache',()=>{
 const ids=[0,1,2,3,4,5],full=fullAttention(ids);let cache={k:[] as number[][],v:[] as number[][]};
 for(let i=0;i<ids.length;i++){const old=structuredClone(cache);const step=cachedStep(ids[i],cache);assert.deepEqual(cache,old);assert.deepEqual(step.output,full[i].output);assert.deepEqual(fullAttention(ids.slice(0,i+1))[i],full[i]);cache=step.cache;}
});
test('shared diagram numbers match the hand calculation, softmax stays normalized',()=>{
 const a=fullAttention([0,1])[1];assert(Math.abs(a.weights[0]-.33023845)<1e-7);assert(Math.abs(a.output[0]-.6604769)<1e-7);assert(Math.abs(a.output[1]-.66976155)<1e-7);
 const probabilities=softmax([10000,10001]);assert(Math.abs(probabilities.reduce((a,b)=>a+b,0)-1)<1e-14);
 assert(Math.abs(model.candidateProbabilities.reduce((a,b)=>a+b,0)-1)<1e-14);
});
test('gradient demo shows optimal, improving and overshooting steps',()=>{
 assert.deepEqual(gradientUpdate(0),{next:2,loss:4});assert.equal(gradientUpdate(.125).loss,0);assert(Math.abs(gradientUpdate(.1).loss-.16)<1e-12);assert.equal(gradientUpdate(1).loss,196);assert.throws(()=>gradientUpdate(NaN));
 assert.throws(()=>cachePolicy(-1,'lru'));assert.throws(()=>selectDevices(-1,false));
});
