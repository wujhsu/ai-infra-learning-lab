"""Masked elementwise add: correctness first, then CUDA-event timing. GPU unverified."""
import json, statistics
import torch
import triton
import triton.language as tl

@triton.jit
def add_kernel(X, Y, Z, N: tl.constexpr, BLOCK: tl.constexpr):
    offsets = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < N
    x = tl.load(X + offsets, mask=mask, other=0)
    y = tl.load(Y + offsets, mask=mask, other=0)
    tl.store(Z + offsets, x + y, mask=mask)

def add(x, y):
    assert x.is_cuda and y.is_cuda and x.is_contiguous() and y.is_contiguous()
    assert x.shape == y.shape and x.dtype == y.dtype and x.device == y.device
    z = torch.empty_like(x)
    if x.numel():
        add_kernel[(triton.cdiv(x.numel(), 256),)](x, y, z, x.numel(), 256)
    return z

def timed(fn, repeats=30):
    for _ in range(10): fn()
    torch.cuda.synchronize()
    samples=[]
    for _ in range(repeats):
        start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
        start.record()
        for _ in range(100): fn()
        end.record();end.synchronize();samples.append(start.elapsed_time(end)/100)
    return {"median_ms":statistics.median(samples),"min_ms":min(samples),"max_ms":max(samples),"samples_ms":samples}

if __name__ == '__main__':
    if not torch.cuda.is_available(): raise SystemExit('Requires CUDA GPU; no CPU performance substitute')
    torch.manual_seed(7)
    for n in [0,1,255,256,257,100003]:
        x=torch.randn(n,device='cuda');y=torch.randn_like(x)
        torch.testing.assert_close(add(x,y),x+y)
    x=torch.randn(1048576,device='cuda');y=torch.randn_like(x)
    print(json.dumps({"torch":torch.__version__,"triton":triton.__version__,"gpu":torch.cuda.get_device_name(),"n":x.numel(),"dtype":str(x.dtype),"eager":timed(lambda:x+y),"triton_add":timed(lambda:add(x,y)),"scope":"includes output allocation and launches; not isolated kernel latency"},indent=2))
