"""Short Qwen SFT pipeline check. Authored tiny data is not a quality benchmark.
Run on a CUDA GPU in the pinned environment. No automatic model publishing.
"""
import argparse,json,random
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from peft import LoraConfig,get_peft_model
MODEL='Qwen/Qwen3-0.6B'
REVISION='c1899de289a04d12100db370d81485cdf75e47ca'
DATA=[('把数字二写成阿拉伯数字，只输出结果。','2'),('把数字三写成阿拉伯数字，只输出结果。','3'),('把数字四写成阿拉伯数字，只输出结果。','4'),('把数字五写成阿拉伯数字，只输出结果。','5')]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--steps',type=int,default=8);ap.add_argument('--output',type=Path,default=Path('/tmp/ai-infra-adapter'));args=ap.parse_args()
    if not torch.cuda.is_available():raise SystemExit('CUDA GPU required for this documented route; CPU toy project is separate.')
    if args.steps<1:ap.error('steps must be positive')
    random.seed(7);torch.manual_seed(7)
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,dtype=torch.bfloat16).cuda()
    model.config.use_cache=False
    model=get_peft_model(model,LoraConfig(r=8,lora_alpha=16,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4)
    losses=[]
    for step in range(args.steps):
        question,answer=DATA[step%len(DATA)]
        prefix=tokenizer.apply_chat_template([{'role':'user','content':question}],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        # Use the exact templated prompt IDs then tokenize the answer separately.
        suffix=tokenizer.encode(answer,add_special_tokens=False)+[tokenizer.eos_token_id]
        ids=torch.tensor([prefix+suffix],device='cuda')
        labels=ids.clone();labels[:,:len(prefix)]=-100
        if step==0:print(json.dumps({'prompt_tokens':len(prefix),'target_text':tokenizer.decode(suffix),'target_tokens':len(suffix)},ensure_ascii=False))
        model.train();optimizer.zero_grad(set_to_none=True)
        loss=model(input_ids=ids,labels=labels).loss
        if not torch.isfinite(loss):raise RuntimeError('non-finite loss')
        loss.backward();optimizer.step();losses.append(loss.item())
    args.output.mkdir(parents=True,exist_ok=True)
    model.save_pretrained(args.output);tokenizer.save_pretrained(args.output)
    manifest={'base_model':MODEL,'revision':REVISION,'steps':args.steps,'training_loss':losses,'data':'four authored format examples','quality':'not evaluated','verification':'GPU run result only when actually executed'}
    (args.output/'training-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
