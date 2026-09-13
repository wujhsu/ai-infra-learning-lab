"""Resolve model revision and record immutable experiment inputs. Does not launch a GPU."""
import json,urllib.request,subprocess
from pathlib import Path
MODEL='Qwen/Qwen2.5-0.5B-Instruct'
with urllib.request.urlopen('https://huggingface.co/api/models/'+MODEL,timeout=30) as r: revision=json.load(r)['sha']
if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision):raise ValueError('Invalid revision')
image='vllm/vllm-openai:v0.29.0'
Path('experiment.env').write_text(f'MODEL={MODEL}\nMODEL_REVISION={revision}\nIMAGE={image}\n')
Path('environment.json').write_text(json.dumps({'model':MODEL,'revision':revision,'image':image,'hardware_verified':False},indent=2))
print('Wrote experiment.env and environment.json. Next: bash serve.sh')
