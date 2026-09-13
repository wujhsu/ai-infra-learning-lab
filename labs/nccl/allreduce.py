"""Run with torchrun --standalone --nproc-per-node=2 allreduce.py."""
import os,json,datetime,torch,torch.distributed as dist
local=int(os.environ['LOCAL_RANK']);torch.cuda.set_device(local)
dist.init_process_group('nccl',timeout=datetime.timedelta(seconds=90))
try:
 rank=dist.get_rank();world=dist.get_world_size();x=torch.tensor([rank+1.,2*(rank+1.)],device='cuda')
 dist.all_reduce(x,op=dist.ReduceOp.SUM)
 expected=torch.tensor([world*(world+1)/2,world*(world+1)],device='cuda')
 torch.testing.assert_close(x,expected)
 print(json.dumps({'rank':rank,'world':world,'value':x.tolist(),'expected':expected.tolist(),'nccl':torch.cuda.nccl.version(),'torch':torch.__version__}))
finally:dist.destroy_process_group()
