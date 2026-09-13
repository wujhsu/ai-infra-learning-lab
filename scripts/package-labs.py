"""Package only reviewed lab sources; never local results, environments or caches."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
allowed={'.py','.sh','.yaml','.yml','.md','.txt'}
target=root/'public/downloads/labs.zip';target.parent.mkdir(exist_ok=True,parents=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted((root/'labs').rglob('*')):
  if not any(part in {'.venv','__pycache__','results'} for part in file.parts) and file.is_file() and (file.suffix in allowed or file.name.endswith('Dockerfile')):
   archive.write(file,file.relative_to(root))
print(f'Packaged {target.name}')
