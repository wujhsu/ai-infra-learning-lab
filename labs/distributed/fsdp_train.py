"""FSDP2 CUDA teaching route; requires >=2 GPUs; not CPU-verified."""
import os,sys,datetime,json
from pathlib import Path
import torch
import torch.distributed as dist
from torch.distributed.fsdp import fully_shard
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tiny_model'))
from model import TinyLM,Config
local=int(os.environ['LOCAL_RANK']);torch.cuda.set_device(local)
dist.init_process_group('nccl',timeout=datetime.timedelta(seconds=120))
try:
    torch.manual_seed(7)
    model=TinyLM(Config(width=128,heads=4,layers=4)).cuda()
    for block in model.blocks:fully_shard(block)
    fully_shard(model)
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001)
    x=torch.tensor([[0,1,2,3,4,5]],device='cuda');y=torch.tensor([[1,2,3,4,5,6]],device='cuda')
    for step in range(10):
        optimizer.zero_grad(set_to_none=True)
        logits,_=model(x)
        loss=torch.nn.functional.cross_entropy(logits.reshape(-1,7),y.reshape(-1))
        loss.backward();optimizer.step()
    torch.cuda.synchronize()
    print(json.dumps({'rank':dist.get_rank(),'loss':loss.item(),'peak_bytes':torch.cuda.max_memory_allocated(),'torch':torch.__version__}))
finally:dist.destroy_process_group()
