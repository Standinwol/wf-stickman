#!/usr/bin/env python3
"""Validate manifests using only Python's standard library; no generation calls."""
from pathlib import Path
import json,hashlib,argparse,zipfile
def validate(root):
    read=lambda p:json.loads((root/p).read_text(encoding='utf-8-sig'))
    master=read('master-workflow.json');errors=[];all_ids=[]
    if master['batch_size']!=6:errors.append('Unexpected batch size')
    for batch in master['batches']:
        data=read(batch['file']);ids=[s['id'] for s in data['scenes']]
        if not 1<=len(ids)<=6 or ids!=batch['scene_ids']:errors.append('Batch membership mismatch: '+batch['batch_id'])
        for s in data['scenes']:
            if s['kind']!='story' or s['media_strategy']!='muse_generate_image_then_video':errors.append('A ready graphic/reuse was sent for generation')
            if not s['image_prompt_en'].endswith(read('common/creative-bible.json')['fixed_style_en_exact']):errors.append('Fixed style changed: '+s['id'])
            if s['source_clip_seconds']!=10 or not 0<s['duration_frames']<=300:errors.append('Bad measured clip timing: '+s['id'])
            if s['image']['prompt_en']!=s['image_prompt_en'] or s['video']['prompt_en']!=s['video_prompt_en']:errors.append('Conflicting prompts: '+s['id'])
            expected=hashlib.sha256((s['id']+'\n'+s['image_prompt_en']+'\n'+s['video_prompt_en']).encode()).hexdigest()
            if expected!=s['idempotency_key']:errors.append('Prompt fingerprint mismatch: '+s['id'])
            for ref in s['image_reference_files']:
                if not any(x['path']==ref for x in read('common/references-manifest.json')):errors.append('Missing reference declaration: '+ref)
        all_ids+=ids
    if len(all_ids)!=141 or len(set(all_ids))!=141:errors.append('New scene coverage is not exactly 141 unique IDs')
    if not master['service_policy']['max_active_generations']==1:errors.append('Generations must be sequential')
    policy=read('dispatch/resume-policy.json');units=read('dispatch/work-units.json')['units']
    if policy['max_scene_ids_per_work_unit']!=2 or policy['max_work_units_per_message']!=1:errors.append('Execution work unit must be two scenes per message')
    if any(not 1<=len(unit['scene_ids'])<=2 for unit in units):errors.append('Oversized execution work unit')
    unit_ids=[sid for unit in units for sid in unit['scene_ids']]
    if sorted(unit_ids)!=sorted(all_ids):errors.append('Work units must cover every scene exactly once')
    if master['service_policy']['max_extra_generation_calls_production']!=12:errors.append('Unexpected shared repair budget')
    for batch in master['batches']:
        if read(batch['file'])['service_policy']!=master['service_policy']:errors.append('Conflicting per-batch retry policy')
    # Full package contains the full storyboard; the bootstrap workspace may omit this optional file.
    if (root/'storyboard.full.json').exists():
        seq=read('storyboard.full.json');cursor=0
        for s in seq:
            if s['from_frame']!=cursor:errors.append('Timeline gap/overlap: '+s['id'])
            cursor+=s['duration_frames']
        if cursor!=master['duration_frames'] or len(seq)!=197:errors.append('Full timeline mismatch')
        if sum(s['media_strategy']=='ready_deterministic_graphic' for s in seq)!=43:errors.append('Ready graphic coverage mismatch')
        if {s['id'] for s in seq if s['media_strategy']=='muse_generate_image_then_video'}!=set(all_ids):errors.append('Batch/full storyboard mismatch')
    for name in ['references','graphics']:
        rows=read(f'common/{name}-manifest.json')
        archive=root/f'common/{name}.zip'
        if archive.exists():
            if archive.stat().st_size>=25000000:errors.append('Common ZIP exceeds 25 MB')
            with zipfile.ZipFile(archive) as z:
                for row in rows:
                    file=row.get('path',row.get('file'));data=z.read(file)
                    if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:errors.append('Archive asset checksum mismatch: '+file)
    return {'ok':not errors,'errors':errors,'batch_count':len(master['batches']),'new_unique_scenes':len(set(all_ids)),'ready_graphics':43,'reused_unique_demo_assets':master['reused_demo_assets'],'duration_seconds':master['measured_planned_duration_seconds'],'checks':['Batch size, coverage and unique IDs','Locked style suffix and complete prompts','Prompt idempotency fingerprints','Actual voice timing and <=10-second shot coverage','No generated jobs for supplied graphics or demo assets','Reference existence declarations','Complete continuous timeline when available','Independent common ZIP sizes and SHA-256']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--report');args=ap.parse_args();result=validate(Path(args.root).resolve())
    if args.report:Path(args.report).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(not result['ok'])
