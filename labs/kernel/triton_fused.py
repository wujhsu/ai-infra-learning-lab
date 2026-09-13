"""Chapter kernel: relu(2*x+1). CUDA-only; correctness before measurements."""
import json,torch,triton
import triton.language as tl
from triton_add import timed
@triton.jit
def fused(X,Y,N:tl.constexpr,BLOCK:tl.constexpr):
    offsets=tl.program_id(0)*BLOCK+tl.arange(0,BLOCK)
    active=offsets<N
    values=tl.load(X+offsets,mask=active,other=0.)
    result=tl.maximum(values*2.+1.,0.)
    tl.store(Y+offsets,result,mask=active)
def run(x):
    assert x.is_cuda and x.is_contiguous()
    y=torch.empty_like(x)
    if x.numel():fused[(triton.cdiv(x.numel(),256),)](x,y,x.numel(),256)
    return y
if __name__=='__main__':
    if not torch.cuda.is_available():raise SystemExit('CUDA GPU required; execution is not verified on CPU')
    torch.manual_seed(7);rows=[]
    for n in [0,1,255,256,257,1000,1048576]:
        x=torch.randn(n,device='cuda');expected=(2*x+1).relu()
        torch.testing.assert_close(run(x),expected)
        if n:rows.append({'n':n,'eager':timed(lambda:(2*x+1).relu()),'triton':timed(lambda:run(x))})
    print(json.dumps({'gpu':torch.cuda.get_device_name(),'torch':torch.__version__,'triton':triton.__version__,'dtype':'float32','rows':rows,'scope':'allocation and launch included; first compilation excluded'},indent=2))
