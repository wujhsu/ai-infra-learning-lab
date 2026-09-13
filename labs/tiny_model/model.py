"""Readable two-layer causal Transformer. CPU teaching baseline, no dropout.
Tensor convention: batch B, time T, model width C; heads H and head width D.
The model is intentionally small; it is not an implementation of Qwen.
"""
from dataclasses import dataclass, asdict
import math
import torch
from torch import nn

@dataclass
class Config:
    vocab_size: int = 7
    width: int = 32
    heads: int = 2
    layers: int = 2
    max_context: int = 32

class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.heads, self.head_width = cfg.heads, cfg.width // cfg.heads
        self.norm1 = nn.LayerNorm(cfg.width)
        self.qkv = nn.Linear(cfg.width, 3 * cfg.width, bias=False)
        self.out = nn.Linear(cfg.width, cfg.width, bias=False)
        self.norm2 = nn.LayerNorm(cfg.width)
        self.mlp = nn.Sequential(nn.Linear(cfg.width, 4*cfg.width), nn.GELU(), nn.Linear(4*cfg.width, cfg.width))

    def forward(self, x, past=None):
        batch, time, width = x.shape
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)
        def split(t):
            return t.view(batch, time, self.heads, self.head_width).transpose(1, 2)
        q, k, v = map(split, (q, k, v))
        old = 0 if past is None else past[0].shape[-2]
        if past is not None:
            k = torch.cat((past[0], k), dim=-2)
            v = torch.cat((past[1], v), dim=-2)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_width)
        query_positions = torch.arange(old, old + time, device=x.device)[:, None]
        key_positions = torch.arange(old + time, device=x.device)[None, :]
        scores = scores.masked_fill(key_positions > query_positions, float('-inf'))
        probabilities = torch.softmax(scores, dim=-1)
        mixed = (probabilities @ v).transpose(1, 2).contiguous().view(batch, time, width)
        x = x + self.out(mixed)
        x = x + self.mlp(self.norm2(x))
        return x, (k, v)

class TinyLM(nn.Module):
    def __init__(self, cfg=Config()):
        super().__init__()
        if cfg.width % cfg.heads:
            raise ValueError('width must divide into equal heads')
        self.cfg = cfg
        self.token_embedding = nn.Embedding(cfg.vocab_size, cfg.width)
        self.position_embedding = nn.Embedding(cfg.max_context, cfg.width)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.layers)])
        self.norm = nn.LayerNorm(cfg.width)
        self.head = nn.Linear(cfg.width, cfg.vocab_size, bias=False)

    def forward(self, ids, cache=None):
        past = 0 if cache is None else cache[0][0].shape[-2]
        if past + ids.shape[1] > self.cfg.max_context:
            raise ValueError('context exceeds configured position table')
        positions = torch.arange(past, past + ids.shape[1], device=ids.device)
        x = self.token_embedding(ids) + self.position_embedding(positions)
        updated = []
        for i, block in enumerate(self.blocks):
            x, kv = block(x, None if cache is None else cache[i])
            updated.append(kv)
        return self.head(self.norm(x)), updated

    @torch.no_grad()
    def generate(self, ids, max_new_tokens=8, eos_id=6, use_cache=True):
        self.eval()
        result = ids.clone()
        cache = None
        for _ in range(max_new_tokens):
            model_input = result if cache is None or not use_cache else result[:, -1:]
            logits, new_cache = self(model_input, cache if use_cache else None)
            next_id = logits[:, -1].argmax(-1, keepdim=True)
            result = torch.cat((result, next_id), dim=1)
            cache = new_cache if use_cache else None
            if (next_id == eos_id).all():
                break
        return result

def save_checkpoint(path, model, optimizer, step):
    torch.save({'config':asdict(model.cfg),'model':model.state_dict(),
                'optimizer':optimizer.state_dict(),'step':step,'rng':torch.get_rng_state()}, path)

def load_checkpoint(path):
    data = torch.load(path, map_location='cpu', weights_only=True)
    model = TinyLM(Config(**data['config']))
    model.load_state_dict(data['model'])
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
    optimizer.load_state_dict(data['optimizer'])
    torch.set_rng_state(data['rng'])
    return model, optimizer, data['step']
