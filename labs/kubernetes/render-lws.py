"""Generate a two-node / one-GPU-per-node vLLM LWS example as Kubernetes JSON.

Schema and flags checked against LWS 0.10.0 and vLLM 0.29.0 source.
Hardware execution has NOT been verified on this workstation.
"""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--model-revision',required=True)
p.add_argument('--image',default='vllm/vllm-openai:v0.29.0');a=p.parse_args()
if not re.fullmatch('[0-9a-f]{40}',a.model_revision):p.error('Use the exact Hugging Face commit from prepare.py')
namespace='inference-lws-lab';name='vllm-lab'
check=(Path(__file__).parents[1]/'nccl/allreduce.py').read_text()
common='''set -eu
test -n "$LWS_LEADER_ADDRESS"
test -n "$LWS_WORKER_INDEX"
nvidia-smi
torchrun --nnodes="$LWS_GROUP_SIZE" --nproc-per-node=1 --node-rank="$LWS_WORKER_INDEX" --master-addr="$LWS_LEADER_ADDRESS" --master-port=29501 /lab/allreduce.py
touch /tmp/preflight-passed
exec vllm serve Qwen/Qwen2.5-0.5B-Instruct --revision "$MODEL_REVISION" --served-model-name lab-model --host 0.0.0.0 --port 8000 --max-model-len 2048 --gpu-memory-utilization 0.8 --tensor-parallel-size 1 --pipeline-parallel-size 2 --distributed-executor-backend mp --data-parallel-backend mp --nnodes "$LWS_GROUP_SIZE" --node-rank "$LWS_WORKER_INDEX" --master-addr "$LWS_LEADER_ADDRESS" --master-port 29500'''
def template(leader):
 container={'name':'engine','image':a.image,'command':['bash','-c',common+('' if leader else ' --headless')],
  'env':[{'name':'MODEL_REVISION','value':a.model_revision},{'name':'NCCL_DEBUG','value':'INFO'}],
  'resources':{'requests':{'cpu':'2','memory':'8Gi'},'limits':{'nvidia.com/gpu':'1','memory':'16Gi'}},
  'volumeMounts':[{'name':'shm','mountPath':'/dev/shm'},{'name':'lab','mountPath':'/lab'}]}
 if leader:
  container.update({'ports':[{'containerPort':8000}],
   'startupProbe':{'httpGet':{'path':'/health','port':8000},'periodSeconds':10,'failureThreshold':90},
   'readinessProbe':{'httpGet':{'path':'/health','port':8000},'periodSeconds':5}})
 else:
  container['readinessProbe']={'exec':{'command':['test','-f','/tmp/preflight-passed']},'periodSeconds':5}
 return {'metadata':{'labels':{'app':name,'role':'leader' if leader else 'worker'}},'spec':{
  'affinity':{'podAntiAffinity':{'requiredDuringSchedulingIgnoredDuringExecution':[{'labelSelector':{'matchLabels':{'app':name}},'topologyKey':'kubernetes.io/hostname'}]}},
  'containers':[container],'volumes':[{'name':'shm','emptyDir':{'medium':'Memory','sizeLimit':'2Gi'}},{'name':'lab','configMap':{'name':'collective-preflight'}}]}}
items=[{'apiVersion':'v1','kind':'Namespace','metadata':{'name':namespace}},
 {'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'collective-preflight','namespace':namespace},'data':{'allreduce.py':check}},
 {'apiVersion':'leaderworkerset.x-k8s.io/v1','kind':'LeaderWorkerSet','metadata':{'name':name,'namespace':namespace},'spec':{'replicas':1,'startupPolicy':'LeaderCreated','leaderWorkerTemplate':{'size':2,'restartPolicy':'RecreateGroupOnPodRestart','leaderTemplate':template(True),'workerTemplate':template(False)}}},
 {'apiVersion':'v1','kind':'Service','metadata':{'name':name,'namespace':namespace},'spec':{'selector':{'app':name,'role':'leader'},'ports':[{'port':8000,'targetPort':8000}]}}]
print(json.dumps({'apiVersion':'v1','kind':'List','items':items},indent=2))
