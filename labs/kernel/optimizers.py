"""Compare public AdamW paths with fresh, identical inputs and states."""
import json,time,torch
assert torch.cuda.is_available()
results={}
for name,kwargs in [('single',{'foreach':False,'fused':False}),('foreach',{'foreach':True,'fused':False}),('fused',{'fused':True})]:
 torch.manual_seed(123);p=torch.nn.Parameter(torch.randn(1024,1024,device='cuda'));opt=torch.optim.AdamW([p],lr=.001,**kwargs)
 losses=[]
 for step in range(120):
  if step==20:torch.cuda.synchronize();start=time.perf_counter();torch.cuda.reset_peak_memory_stats()
  opt.zero_grad(set_to_none=True);loss=(p*p).mean();loss.backward();opt.step()
  if step%20==0:losses.append(float(loss.detach().cpu()))
 torch.cuda.synchronize();results[name]={'step_ms':(time.perf_counter()-start)*1000/100,'peak_bytes':torch.cuda.max_memory_allocated(),'loss_samples':losses}
 del opt,p,loss;torch.cuda.empty_cache()
print(json.dumps(results,indent=2))
