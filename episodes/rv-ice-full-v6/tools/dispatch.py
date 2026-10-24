#!/usr/bin/env python3
"""Report a finite work unit from real checkpoints. Never starts a Muse turn."""
from pathlib import Path
import argparse,json

ROOT=Path.cwd().resolve()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def next_unit(root):
    master=read(root/'master-workflow.json')
    policy=read(root/'dispatch/resume-policy.json')
    limit=policy['max_scene_ids_per_work_unit'];pending=[];repairs=[];unresolved=[]
    states={};jobs={}
    for batch in master['batches']:
        job=read(root/batch['file']);jobs[batch['batch_id']]=job
        path=root/job['checkpoint']['progress'];state=read(path) if path.exists() else {'scenes':{}}
        states[batch['batch_id']]=state
        for scene in job['scenes']:
            row=state['scenes'].get(scene['id'],{})
            item={'batch_id':batch['batch_id'],'batch_file':batch['file'],'scene_id':scene['id']}
            if row.get('running'):unresolved.append(dict(item,running=row['running']))
            elif row.get('status') in ['failed','needs_review']:
                stage=row.get('failed_stage') if row['status']=='failed' else 'video' if row.get('video') and not row['video'].get('visual_qa',{}).get('ok') else 'image'
                if 0<row.get('attempts',{}).get(stage,0)<job['service_policy'].get('max_new_'+stage+'_calls_per_scene',1):
                    repairs.append(dict(item,stage=stage,reason=row.get('error') or row.get(stage,{}).get('visual_qa',{})))
            elif row.get('status')!='blocked' and not (row.get('status')=='video_ready' and row.get('video')):
                pending.append(dict(item,stage='video' if row.get('image') else 'image'))
    if unresolved:return {'action':'resume_existing_job_only','jobs':unresolved,'do_not_resubmit':True}
    # Preserve active forward progress; bounded repairs are queued after first-pass assets.
    if pending:
        active=pending[0]['batch_id'];selected=[p for p in pending if p['batch_id']==active][:limit]
        return {'action':'execute_work_unit','max_scene_ids':limit,'scenes':selected,'remaining_first_pass_scene_ids':len(pending),'repair_candidates':repairs,'then':'Checkpoint and package the affected delivery batch. Another Muse message is required if this message ends.'}
    used=sum(max(0,n-1) for state in states.values() for row in state['scenes'].values() for n in row.get('attempts',{}).values())
    if repairs and used<master['service_policy']['max_extra_generation_calls_production']:
        return {'action':'prepare_bounded_repairs','scenes':repairs[:min(limit,master['service_policy']['max_extra_generation_calls_production']-used)],'extra_calls_used':used}
    statuses={bid:{sid:row['status'] for sid,row in state['scenes'].items()} for bid,state in states.items()}
    complete=all(len(states[b['batch_id']]['scenes'])==len(b['scene_ids']) and all(row['status']=='video_ready' and row.get('video') for row in states[b['batch_id']]['scenes'].values()) for b in master['batches'])
    return {'action':'complete' if complete else 'report_remaining_review_or_blocked','statuses':statuses,'extra_calls_used':used}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['next']);args=parser.parse_args()
    print(json.dumps(next_unit(ROOT),ensure_ascii=False,indent=2))
