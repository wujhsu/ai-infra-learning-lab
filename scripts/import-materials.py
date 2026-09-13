"""Explicit local-only import. Never used by CI; publish selected slides, not minutes."""
import json,re,subprocess,hashlib
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1]
archive=root.parent/'kubecon-china-2026-notes'
slides=[]; sessions=[]; jobs=[]
selection={'advanced-nccl':[5,9,14,20,21,23,24,27,32], 'kernelagent':[7,9,11,13,15,16], 'self-healing-rollouts':[8,12,17,20,25], 'speedy-optimizers':[2,3,4,5,7,11], 'lws-preflight':[4,5,6,7,9,10], 'llm-observability':[5,7,9,11,12,13,14,15], 'pytorch-generalization':[5,8,12,15], 'kubernetes-dra':[9,12,13,21,23,34,44], '2026-09-08-keynotes':[8,10]}
# Parse only known public fields from the archive manifest. No minute tokens copied.
manifest=(archive/'manifest.yaml').read_text()
chunks=re.split(r'^  - id: ',manifest,flags=re.M)[1:]
for chunk in chunks:
 sid=chunk.splitlines()[0].strip()
 def field(name):
  m=re.search(r'^    '+name+r': (.+)$',chunk,re.M)
  return m.group(1).strip().strip('"') if m else ''
 path=archive/field('path')
 readme=(path/'README.md').read_text()
 title=field('official_title')
 summary=readme.split('## 核心摘要')[-1].split('\n## ')[0].strip() if '## 核心摘要' in readme else '上午短场次按主题整理；录音并不覆盖全部官方时段。'
 sessions.append({'id':sid,'title':title,'date':field('path').split('/')[0],'time':field('official_time'),'summary':summary,'speakers':field('speakers').strip('[]'),'hasSlides':bool(list((path/'materials').glob('*')))})
 if not (path/'materials').exists(): continue
 for file in (path/'materials').iterdir():
  if file.suffix not in ['.pdf','.pptx']:continue
  pdf=file if file.suffix=='.pdf' else root.parent/'tmp/learning-pptx'/(file.stem+'.pdf')
  text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode('utf-8')
  pages=text.split('\f'); pages=pages[:-1] if not pages[-1].strip() else pages
  notes=(path/'slides-notes.md').read_text()
  note_map={int(a):b for a,b in re.findall(r'^(\d+)\. \*\*(.+)$',notes,re.M)}
  for n,content in enumerate(pages,1):
   clean=re.sub(r'\S+@\S+','[联系方式略]',content).strip()
   desc=note_map.get(n,'').replace('**','')
   if not desc:
    m=re.search(r'## 第 '+str(n)+r' 页[：:]([^\n]+)',notes)
    desc=m.group(1).strip() if m else next((l.strip() for l in clean.splitlines() if l.strip()),'讲义页')
   chosen=n in selection.get(sid,[])
   slides.append({'id':f'{sid}-{n}','session':sid,'page':n,'title':desc.split('：')[0][:120],'description':desc,'text':clean,'selected':chosen,'image':f'slides/{sid}-{n}.webp' if chosen else None,'highres':f'slides/{sid}-{n}-large.webp' if chosen else None,'sourceFile':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
   if chosen: jobs.append((pdf,sid,n))
def render(job):
 pdf,sid,n=job
 prefix=root.parent/'tmp'/f'learning-{sid}-{n}'
 subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-scale-to','2400','-singlefile','-png',str(pdf),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(str(prefix)+'.png').convert('RGB')
 im.save(root/'public/slides'/f'{sid}-{n}-large.webp','WEBP',quality=91)
 im.thumbnail((1200,1200));im.save(root/'public/slides'/f'{sid}-{n}.webp','WEBP',quality=87)
 prefix.with_suffix('.png').unlink()
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,jobs))
(root/'src/data/slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2))
(root/'src/data/sessions.json').write_text(json.dumps(sessions,ensure_ascii=False,indent=2))
assert len(slides)==214, f'Expected 214, got {len(slides)}'
print(f'Indexed {len(slides)} pages; rendered {len(jobs)} selected pages; {len(sessions)} sessions.')
