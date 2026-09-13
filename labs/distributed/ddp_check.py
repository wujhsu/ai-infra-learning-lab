"""Compare one global-batch update against DDP shard updates (CPU default)."""
import os, sys, copy, json, datetime
from pathlib import Path
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tiny_model'))
from model import TinyLM

def main():
    use_cuda=os.environ.get('LAB_DEVICE','cpu')=='cuda'
    local=int(os.environ['LOCAL_RANK'])
    if use_cuda:torch.cuda.set_device(local)
    device=torch.device('cuda',local) if use_cuda else torch.device('cpu')
    torch.set_num_threads(1);torch.manual_seed(7)
    dist.init_process_group('nccl' if use_cuda else 'gloo',timeout=datetime.timedelta(seconds=90))
    try:
        rank,world=dist.get_rank(),dist.get_world_size()
        if 4%world:raise ValueError('world size must divide the four-sample teaching batch')
        model=TinyLM().to(device)
        baseline=copy.deepcopy(model)
        ddp=DDP(model,device_ids=[local] if use_cuda else None)
        x=torch.tensor([[0,1,2],[0,2,1],[1,3,4],[2,4,3]],device=device)
        y=torch.tensor([[1,2,3],[2,1,4],[3,4,5],[4,3,6]],device=device)
        opt_a=torch.optim.SGD(baseline.parameters(),lr=.01)
        opt_b=torch.optim.SGD(ddp.parameters(),lr=.01)
        full_loss=torch.nn.functional.cross_entropy(baseline(x)[0].reshape(-1,7),y.reshape(-1))
        full_loss.backward();opt_a.step()
        indices=torch.arange(rank,4,world,device=device)
        local_loss=torch.nn.functional.cross_entropy(ddp(x[indices])[0].reshape(-1,7),y[indices].reshape(-1))
        local_loss.backward();opt_b.step()
        error=max((a-b).abs().max().item() for a,b in zip(baseline.parameters(),model.parameters()))
        for a,b in zip(baseline.parameters(),model.parameters()):
            torch.testing.assert_close(a,b,atol=2e-6,rtol=2e-5)
        print(json.dumps({'rank':rank,'world':world,'device':str(device),'samples':indices.tolist(),'max_parameter_error':error,'matches_global_batch':True}),flush=True)
    finally:dist.destroy_process_group()
if __name__=='__main__':main()
