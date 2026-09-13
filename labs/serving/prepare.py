"""Resolve model revision and record immutable experiment inputs. Does not launch a GPU."""
import json
from pathlib import Path
MODEL='Qwen/Qwen3-0.6B'
revision='c1899de289a04d12100db370d81485cdf75e47ca'  # Official model revision checked 2026-09-13
if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision):raise ValueError('Invalid revision')
image='vllm/vllm-openai:v0.29.0'
(Path(__file__).resolve().parent/'experiment.env').write_text(f'MODEL={MODEL}\nMODEL_REVISION={revision}\nIMAGE={image}\n')
(Path(__file__).resolve().parent/'environment.json').write_text(json.dumps({'model':MODEL,'revision':revision,'image':image,'hardware_verified':False},indent=2))
print('Wrote experiment.env and environment.json. Next from repository root: bash labs/serving/serve.sh')
