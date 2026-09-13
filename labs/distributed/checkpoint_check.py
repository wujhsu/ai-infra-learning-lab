"""DCP roundtrip and next-step equivalence; CPU/Gloo, same world size, fixed data."""
import os,sys,json,datetime,argparse
from pathlib import Path
import torch
import torch.distributed as dist
import torch.distributed.checkpoint as dcp
from torch.distributed.checkpoint.state_dict import get_state_dict,set_state_dict
from torch.nn.parallel import DistributedDataParallel as DDP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tiny_model'))
from model import TinyLM
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args()
torch.set_num_threads(1)
dist.init_process_group('gloo',timeout=datetime.timedelta(seconds=90))
try:
    torch.manual_seed(7);model=DDP(TinyLM());opt=torch.optim.AdamW(model.parameters(),lr=.01)
    x=torch.tensor([[0,1,2,3,4,5]]);y=torch.tensor([[1,2,3,4,5,6]])
    def step(m,o):
        o.zero_grad(set_to_none=True);logits,_=m(x)
        loss=torch.nn.functional.cross_entropy(logits.reshape(-1,7),y.reshape(-1));loss.backward();o.step()
    step(model,opt)
    ms,osd=get_state_dict(model,opt)
    state={'model':ms,'optimizer':osd,'step':torch.tensor(1)}
    dcp.save(state,checkpoint_id=a.directory)
    step(model,opt)
    expected=[v.detach().clone() for v in model.parameters()]
    torch.manual_seed(99);restored=DDP(TinyLM());restored_opt=torch.optim.AdamW(restored.parameters(),lr=.01)
    ms,osd=get_state_dict(restored,restored_opt)
    loaded={'model':ms,'optimizer':osd,'step':torch.tensor(0)}
    dcp.load(loaded,checkpoint_id=a.directory)
    set_state_dict(restored,restored_opt,model_state_dict=loaded['model'],optim_state_dict=loaded['optimizer'])
    step(restored,restored_opt)
    error=max((a-b).abs().max().item() for a,b in zip(expected,restored.parameters()))
    assert loaded['step'].item()==1 and error<1e-7,(loaded['step'],error)
    print(json.dumps({'rank':dist.get_rank(),'checkpoint_step':1,'next_step_max_error':error,'scope':'CPU DDP fixed data, no dropout, same world size; not elastic recovery'}))
finally:dist.destroy_process_group()
