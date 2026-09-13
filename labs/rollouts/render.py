"""Render a controlled CPU rollout with candidate-only business-path analysis.
No traffic router: replica proportions only approximate request distribution.
"""
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--image',required=True);a=p.parse_args()
ns='inference-rollout-lab'
probe='''import urllib.request,time
success=0
for i in range(10):
 try:
  with urllib.request.urlopen("http://fixture-canary:8000/",timeout=3) as r:
   success+=int(r.status==200)
 except Exception: pass
 time.sleep(1)
print({"samples":10,"success":success},flush=True)
raise SystemExit(0 if success>=9 else 1)
'''
metadata=lambda name:{'name':name,'namespace':ns}
items=[{'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns}}]
for name in ['fixture-stable','fixture-canary']:
 items.append({'apiVersion':'v1','kind':'Service','metadata':metadata(name),'spec':{'selector':{'app':'fixture'},'ports':[{'port':8000,'targetPort':8000}]}})
items.append({'apiVersion':'argoproj.io/v1alpha1','kind':'AnalysisTemplate','metadata':metadata('business-path-check'),'spec':{'metrics':[{'name':'ten-business-requests','failureLimit':0,'provider':{'job':{'spec':{'backoffLimit':0,'activeDeadlineSeconds':60,'template':{'spec':{'restartPolicy':'Never','containers':[{'name':'check','image':'python:3.12.11-alpine','command':['python','-u','-c',probe]}]}}}}}}]}})
items.append({'apiVersion':'argoproj.io/v1alpha1','kind':'Rollout','metadata':metadata('fixture'),'spec':{
 'replicas':5,'revisionHistoryLimit':2,'selector':{'matchLabels':{'app':'fixture'}},
 'strategy':{'canary':{'stableService':'fixture-stable','canaryService':'fixture-canary','steps':[{'setWeight':20},{'analysis':{'templates':[{'templateName':'business-path-check'}]}},{'pause':{}},{'setWeight':100}]}},
 'template':{'metadata':{'labels':{'app':'fixture'}},'spec':{'containers':[{'name':'app','image':a.image,'ports':[{'containerPort':8000}],'env':[{'name':'FAIL','value':'false'},{'name':'LATENCY_SECONDS','value':'0'}],'resources':{'requests':{'cpu':'50m','memory':'32Mi'},'limits':{'cpu':'200m','memory':'64Mi'}},'readinessProbe':{'httpGet':{'path':'/health','port':8000},'periodSeconds':3}}]}}}})
print(json.dumps({'apiVersion':'v1','kind':'List','items':items},indent=2))
