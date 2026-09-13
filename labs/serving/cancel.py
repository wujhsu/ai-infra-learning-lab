"""Close a live stream after first nonempty content. Verify backend cleanup separately."""
import json,urllib.request,time,argparse
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');a=p.parse_args()
payload={'model':'lab-model','messages':[{'role':'user','content':'请详细介绍矩阵乘法，尽量写长一些。'}],'max_tokens':1024,'stream':True,'chat_template_kwargs':{'enable_thinking':False}}
req=urllib.request.Request(a.url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','X-Request-Id':'lab-cancel-check'})
with urllib.request.urlopen(req,timeout=120) as response:
    for line in response:
        if not line.startswith(b'data:'): continue
        data=line[5:].strip()
        if data==b'[DONE]': raise SystemExit('Completed before cancellation; use a longer generation')
        obj=json.loads(data)
        if any(c.get('delta',{}).get('content') for c in obj.get('choices',[])):
            print(json.dumps({'event':'closing_client_stream','time_unix':time.time(),'request_id':'lab-cancel-check','backend_reclamation':'must verify engine metrics/logs; not proven by this script'}));break
    else: raise SystemExit('No content received')
