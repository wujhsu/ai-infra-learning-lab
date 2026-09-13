"""Measure client first-content/chunk timing. Chunks are NOT individual tokens."""
import argparse,json,time,urllib.request,urllib.error,concurrent.futures,statistics

def measure(url,model,prompt,max_tokens):
 payload={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':max_tokens,'temperature':0,'stream':True,'stream_options':{'include_usage':True}}
 started=time.perf_counter();chunks=[];usage=None;completed=False
 try:
  req=urllib.request.Request(url.rstrip('/')+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=120) as response:
   for raw in response:
    line=raw.decode().strip()
    if not line.startswith('data:'):continue
    data=line[5:].strip()
    if data=='[DONE]':
     completed=True;break
    item=json.loads(data)
    if item.get('usage'):usage=item['usage']
    for choice in item.get('choices',[]):
     content=choice.get('delta',{}).get('content')
     if content:chunks.append({'seconds':time.perf_counter()-started,'text':content})
  ended=time.perf_counter()-started
  return {'ok':bool(chunks) and completed,'error':('Stream ended before [DONE]' if not completed else None if chunks else 'No nonempty content'),'first_content_seconds':chunks[0]['seconds'] if chunks else None,'total_seconds':ended,'chunks':chunks,'usage':usage}
 except Exception as e:return {'ok':False,'error':str(e),'total_seconds':time.perf_counter()-started,'chunks':chunks}

def main():
 p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');p.add_argument('--model',default='lab-model');p.add_argument('--requests',type=int,default=20);p.add_argument('--concurrency',type=int,default=1);p.add_argument('--max-tokens',type=int,default=64);p.add_argument('--repeat-input',type=int,default=1);p.add_argument('--output',default='measurements.jsonl');a=p.parse_args()
 if min(a.requests,a.concurrency,a.max_tokens,a.repeat_input)<1:p.error('Counts must be positive')
 prompt=('缓存保存中间结果以避免重复计算。'*a.repeat_input)+'请用三句话解释这个原理。'
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.concurrency) as pool,open(a.output,'w') as f:
  futures=[pool.submit(measure,a.url,a.model,prompt,a.max_tokens) for _ in range(a.requests)]
  rows=[]
  for i,future in enumerate(concurrent.futures.as_completed(futures)):
   row={'request_index':i,'config':vars(a),**future.result()};rows.append(row);f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
 values=sorted(r['first_content_seconds'] for r in rows if r['ok'])
 print(json.dumps({'requests':len(rows),'errors':sum(not r['ok'] for r in rows),'first_content_median':statistics.median(values) if values else None,'first_content_p95_nearest_rank':values[max(0,__import__('math').ceil(.95*len(values))-1)] if values else None,'note':'Closed-loop fixed concurrency; chunk timing is not token ITL. p95 unstable with small sample.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
