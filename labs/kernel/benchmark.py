"""GPU-required benchmark: correctness first; independent candidates; events + medians."""
import json,statistics,torch
assert torch.cuda.is_available(),'A CUDA GPU is required; no fabricated fallback results.'
x=torch.randn(2048,2048,device='cuda')
def baseline(x):return torch.relu(x*2+1)
compiled=torch.compile(baseline)
expected=baseline(x);torch.testing.assert_close(compiled(x),expected)
results={}
for name,fn in [('eager',baseline),('compiled',compiled)]:
 for _ in range(20):fn(x)
 torch.cuda.synchronize();samples=[]
 for _ in range(30):
  start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
  start.record()
  for _ in range(100):fn(x)
  end.record();end.synchronize();samples.append(start.elapsed_time(end)/100)
 results[name]={'median_ms':statistics.median(samples),'samples_ms':samples}
print(json.dumps({'torch':torch.__version__,'gpu':torch.cuda.get_device_name(),'shape':list(x.shape),'dtype':str(x.dtype),'results':results},indent=2))
