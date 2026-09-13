"""Overfit one teaching sentence to verify training, not to claim generalization."""
import argparse, json
from pathlib import Path
import torch
from torch.nn import functional as F
from model import TinyLM, save_checkpoint, load_checkpoint

TOKENS = ['北京','是','中国','的','首都','。','<结束>']
INPUT = torch.tensor([[0,1,2,3,4,5]], dtype=torch.long)
TARGET = torch.tensor([[1,2,3,4,5,6]], dtype=torch.long)

def train_step(model, optimizer):
    model.train()
    optimizer.zero_grad(set_to_none=True)
    logits, _ = model(INPUT)
    loss = F.cross_entropy(logits.reshape(-1, len(TOKENS)), TARGET.reshape(-1))
    loss.backward()
    optimizer.step()
    return loss.item()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--steps', type=int, default=100, help='Total target steps, not extra steps')
    ap.add_argument('--output', type=Path, default=Path('tiny-checkpoint.pt'))
    ap.add_argument('--resume', type=Path)
    args = ap.parse_args()
    if args.steps < 1:
        ap.error('steps must be positive')
    torch.set_num_threads(1)
    torch.manual_seed(7)
    if args.resume:
        model, optimizer, start = load_checkpoint(args.resume)
    else:
        model = TinyLM()
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
        start = 0
    before = F.cross_entropy(model(INPUT)[0].reshape(-1, 7), TARGET.reshape(-1)).item()
    for step in range(start, args.steps):
        train_step(model, optimizer)
    model.eval()
    with torch.no_grad():
        after = F.cross_entropy(model(INPUT)[0].reshape(-1, 7), TARGET.reshape(-1)).item()
        cached = model.generate(torch.tensor([[0,1,2,3]]), use_cache=True)
        full = model.generate(torch.tensor([[0,1,2,3]]), use_cache=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(args.output, model, optimizer, max(start,args.steps))
    print(json.dumps({'torch':torch.__version__,'device':'cpu','start_step':start,
       'end_step':max(start,args.steps),'training_loss_before':before,'training_loss_after':after,
       'generated_ids':cached.tolist(),'text':''.join(TOKENS[i] for i in cached[0].tolist()),
       'cache_generation_equal':torch.equal(cached,full),'evaluation':'one-sentence overfit sanity check; not held-out quality'},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
