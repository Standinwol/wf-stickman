#!/usr/bin/env python3
"""Download only this production's small manifests/common inputs at a pinned commit."""
from pathlib import Path
import argparse,json,urllib.request,hashlib,zipfile,os

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base-url',required=True);ap.add_argument('--root',default='workspace/rv-ice-full-v6');args=ap.parse_args()
    base=args.base_url.rstrip('/')+'/'
    if not base.startswith('https://raw.githubusercontent.com/Standinwol/wf-stickman/'):raise ValueError('Unexpected repository URL')
    revision=base.split('/wf-stickman/',1)[1].split('/',1)[0]
    if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision):raise ValueError('Use a full pinned Git commit, never a moving branch')
    root=Path(args.root).resolve();root.mkdir(parents=True,exist_ok=True)
    def download(name,expected=None):
        dest=(root/name).resolve()
        if not dest.is_relative_to(root):raise ValueError('Invalid destination')
        if dest.exists() and expected and hashlib.sha256(dest.read_bytes()).hexdigest()==expected['sha256']:return dest
        with urllib.request.urlopen(base+name,timeout=90) as response:content=response.read()
        if expected and (len(content)!=expected['bytes'] or hashlib.sha256(content).hexdigest()!=expected['sha256']):raise ValueError('Checksum mismatch: '+name)
        dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_suffix(dest.suffix+'.download');tmp.write_bytes(content);os.replace(tmp,dest);return dest
    checks=json.loads(download('checksums.json').read_text(encoding='utf-8'))['files']
    master=json.loads(download('master-workflow.json',checks['master-workflow.json']).read_text(encoding='utf-8'))
    names=['common/creative-bible.json','common/references.zip','common/references-manifest.json','common/graphics.zip','common/graphics-manifest.json','common/reuse-existing.json','tools/checkpoint.py','tools/dispatch.py','tools/update_runner.py','tools/validate_package.py','dispatch/resume-policy.json','dispatch/work-units.json','dispatch/repair-plan.json','RESUME.vi.md','state/master-progress.seed.json']+[b['file'] for b in master['batches']]
    for name in names:download(name,checks[name])
    for name in ['common/references.zip','common/graphics.zip']:
        with zipfile.ZipFile(root/name) as z:
            for item in z.infolist():
                dest=(root/item.filename).resolve()
                if not dest.is_relative_to(root):raise ValueError('Archive path escapes production root')
            z.extractall(root)
    for name in ['references','graphics']:
        rows=json.loads((root/f'common/{name}-manifest.json').read_text(encoding='utf-8'))
        for row in rows:
            p=root/row.get('path',row.get('file'))
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Extracted asset mismatch: '+str(p))
    state=root/'state/master-progress.json'
    if not state.exists():state.write_bytes((root/'state/master-progress.seed.json').read_bytes())
    print(json.dumps({'ok':True,'root':str(root),'commit':revision,'batches':len(master['batches']),'start':'B001','existing_checkpoints_preserved':True},indent=2))
if __name__=='__main__':main()
