#!/usr/bin/env python3
"""Apply a verified compatible runner revision without touching output/checkpoints."""
from pathlib import Path
import argparse,json,urllib.request,hashlib,os

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',required=True);parser.add_argument('--root',default='.');args=parser.parse_args()
    base=args.base_url.rstrip('/')+'/'
    prefix='https://raw.githubusercontent.com/Standinwol/wf-stickman/'
    if not base.startswith(prefix):raise ValueError('Unexpected repository URL')
    revision=base[len(prefix):].split('/',1)[0]
    if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision):raise ValueError('Use a pinned forty-character commit')
    root=Path(args.root).resolve()
    if not (root/'master-workflow.json').is_file():raise ValueError('Run inside the existing production workspace')
    def fetch(name):
        with urllib.request.urlopen(base+name,timeout=60) as response:return response.read()
    checksum_bytes=fetch('checksums.json');checks=json.loads(checksum_bytes)['files']
    def verified(name):
        data=fetch(name);expected=checks[name]
        if len(data)!=expected['bytes'] or hashlib.sha256(data).hexdigest()!=expected['sha256']:raise ValueError('Checksum mismatch: '+name)
        return data
    master_bytes=verified('master-workflow.json');master=json.loads(master_bytes)
    names=['tools/checkpoint.py','tools/dispatch.py','tools/validate_package.py','tools/update_runner.py','dispatch/resume-policy.json','dispatch/work-units.json','dispatch/repair-plan.json','RUN-MUSE.vi.txt','RESUME.vi.md']+[b['file'] for b in master['batches']]
    contents={name:verified(name) for name in names};contents['master-workflow.json']=master_bytes
    for batch in master['batches']:
        incoming=json.loads(contents[batch['file']]);ids={s['id']:s['idempotency_key'] for s in incoming['scenes']}
        local=root/batch['file']
        if local.exists() and {s['id']:s['idempotency_key'] for s in json.loads(local.read_text(encoding='utf-8-sig'))['scenes']}!=ids:raise ValueError('Incompatible source prompt revision')
        checkpoint=root/incoming['checkpoint']['progress']
        if checkpoint.exists():
            state=json.loads(checkpoint.read_text(encoding='utf-8-sig'))
            if state['job_id']!=incoming['job_id'] or any(ids.get(sid)!=row['idempotency_key'] for sid,row in state['scenes'].items()):raise ValueError('Incompatible live checkpoint')
    # Every download and compatibility check completes before the first write.
    for name,data in dict(contents,**{'checksums.json':checksum_bytes}).items():
        dest=(root/name).resolve()
        if not dest.is_relative_to(root) or name.startswith(('outputs/','deliveries/','state/')):raise ValueError('Unsafe runner destination')
        dest.parent.mkdir(parents=True,exist_ok=True);temp=dest.with_suffix(dest.suffix+'.update');temp.write_bytes(data);os.replace(temp,dest)
    print(json.dumps({'ok':True,'runner_commit':revision,'source_prompts_unchanged':True,'outputs_and_checkpoints_untouched':True,'next_command':'python tools/dispatch.py next'},indent=2))

if __name__=='__main__':main()
