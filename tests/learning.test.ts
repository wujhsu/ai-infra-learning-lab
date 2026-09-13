import test from 'node:test';
import assert from 'node:assert/strict';
import {latency,kvBytes,overlap,batching,cacheBenefit,cachePolicy,selectDevices} from '../src/lib/simulations';
import {emptyStore,emptyEntry,validateStore,mergeStores} from '../src/lib/storage';

test('TTFT excludes subsequent decode; one-token response ends at TTFT',()=>{
 assert.deepEqual(latency(800,600,50,40,32),{ttft:1450,total:2690});
 assert.equal(latency(800,600,50,40,1).total,1450);
 assert.throws(()=>latency(0,1,0,1,NaN));
});
test('KV counts both K and V and uses KV heads; scales with context and concurrency',()=>{
 const one=kvBytes(32,8,128,8192,1,2);
 assert.equal(one,2**30);assert.equal(kvBytes(32,8,128,16384,8,2),one*16);
 assert.throws(()=>kvBytes(32,8,128,0,1,2));
});
test('pipeline pays startup/drain, bounded by the slower stage',()=>{
 assert.deepEqual(overlap(4,3,5),{serial:32,pipelined:23});
 assert.deepEqual(overlap(1,3,5),{serial:8,pipelined:8});
 assert.equal(overlap(4,5,3).pipelined,23);
 assert.throws(()=>overlap(NaN,3,5));
});
test('continuous batching admits C at t2 while static batch waits for A',()=>{
 const continuous=batching(10,2,true),fixed=batching(10,2,false);
 assert(continuous[2].active.includes('C'));assert(!fixed[2].active.includes('C'));
 assert.equal(continuous.find(r=>r.finished.length===4)?.time,6);
 assert.equal(fixed.find(r=>r.finished.length===4)?.time,7);
 for(const r of continuous)assert(r.active.length<=2);
});
test('a cache hit can be slower than recompute; session END frees its blocks',()=>{
 assert.equal(cacheBenefit(4,8,1000,20).savingMs,480);
 assert.equal(cacheBenefit(4,1,1000,20).worthwhile,false);
 assert.equal(cacheBenefit(4,4,1020,20).worthwhile,false);
 assert.throws(()=>cacheBenefit(4,0,1000,20));
 assert.deepEqual(cachePolicy(7,'session').cache,[]);
 assert.deepEqual(cachePolicy(8,'session').cache,['other']);
 assert(cachePolicy(6,'prefix').hits>cachePolicy(6,'lru').hits);
});
test('DRA filters health, memory and topology independently',()=>{
 assert.deepEqual(selectDevices(16,false).map(d=>d.id),['GPU-0','GPU-1']);
 assert.deepEqual(selectDevices(16,true).map(d=>d.id),['GPU-0']);
 assert.deepEqual(selectDevices(48,false).map(d=>d.id),['GPU-0']);
 assert.deepEqual(selectDevices(100,false),[]);
});
test('import rejects future schemas, malformed progress, and unsafe IDs',()=>{
 assert.throws(()=>validateStore({version:2,records:{}}));
 assert.throws(()=>validateStore({version:1,records:{'../x':emptyEntry()}}));
 const s=emptyStore();s.records['learn/01-request']={...emptyEntry(),note:'<script>text only</script>'};
 assert.equal(validateStore(s).records['learn/01-request'].note,'<script>text only</script>');
 assert.throws(()=>validateStore({...s,records:{'learn/01-request':{...emptyEntry(),read:'true'}}}));
});
test('each import conflict mode preserves the expected note and unrelated records',()=>{
 const a=emptyStore(),b=emptyStore();
 a.records['learn/01-request']={...emptyEntry(),note:'local',updated:'2026-09-12T00:00:00Z'};
 b.records['learn/01-request']={...emptyEntry(),note:'import',updated:'2026-09-13T00:00:00Z'};
 b.records['learn/02-kubernetes']=emptyEntry();
 assert.equal(mergeStores(a,b,'newer').records['learn/01-request'].note,'import');
 assert.equal(mergeStores(a,b,'keep').records['learn/01-request'].note,'local');
 assert.equal(mergeStores(b,a,'replace').records['learn/01-request'].note,'local');
 assert.equal(Object.keys(mergeStores(a,b,'keep').records).length,2);
 assert.equal(a.records['learn/01-request'].note,'local');
});
