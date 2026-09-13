"""Propagate a W3C traceparent into a real vLLM request, using only stdlib.

Does not invent a gateway or GPU span. Search returned trace_id in Jaeger.
"""
import argparse,json,secrets,urllib.request,time
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');a=p.parse_args()
trace_id=secrets.token_hex(16);parent_id=secrets.token_hex(8)
req=urllib.request.Request(a.url.rstrip('/')+'/v1/chat/completions',
 data=json.dumps({'model':'lab-model','messages':[{'role':'user','content':'请简短解释 KV Cache。'}],'max_tokens':64}).encode(),
 headers={'Content-Type':'application/json','traceparent':f'00-{trace_id}-{parent_id}-01'})
start=time.perf_counter()
with urllib.request.urlopen(req,timeout=120) as r:result=json.load(r)
print(json.dumps({'trace_id':trace_id,'client_seconds':time.perf_counter()-start,'response':result,'note':'Trace context is propagated; this client does not export its own parent span.'},ensure_ascii=False,indent=2))
