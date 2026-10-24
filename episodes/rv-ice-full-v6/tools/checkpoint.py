#!/usr/bin/env python3
"""Durable per-asset checkpoint helper. Does not call an image/video API."""
from pathlib import Path
import argparse,json,hashlib,subprocess,zipfile,os,datetime,sys,copy
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

ROOT=Path.cwd().resolve()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def safe(value):
    p=(ROOT/value).resolve()
    if not p.is_relative_to(ROOT):raise ValueError('Path escapes the batch workspace')
    return p
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],text=True))
def log(job,state,event):
    state['updated_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(safe(job['checkpoint']['progress']),state)
    journal=safe(job['checkpoint']['journal']);journal.parent.mkdir(parents=True,exist_ok=True)
    with journal.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(time=state['updated_at_utc'],**event),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def init(job):
    path=safe(job['checkpoint']['progress'])
    if path.exists():
        state=read(path)
        if state['job_id']!=job['job_id']:raise ValueError('Wrong existing job checkpoint')
        for s in job['scenes']:
            if state['scenes'][s['id']]['idempotency_key']!=s['idempotency_key']:raise ValueError('Prompt fingerprint changed; use a new explicit revision')
        return state
    state={'job_id':job['job_id'],'batch_id':job['batch_id'],'scenes':{s['id']:{'status':'pending','idempotency_key':s['idempotency_key'],'image':None,'video':None,'running':None,'attempts':{'image':0,'video':0}} for s in job['scenes']}}
    log(job,state,{'event':'initialized'});return state

def inspect_cached(row,stage):
    data=row.get(stage)
    if not data:return False
    p=safe(data['file'])
    if not p.is_file() or digest(p)!=data['sha256']:raise ValueError('Cached asset missing or changed: '+str(p))
    return True

def repair_calls_used():
    return sum(max(0,n-1) for p in safe('outputs').glob('B*/progress.json')
               for row in read(p)['scenes'].values() for n in row.get('attempts',{}).values())

def effective_scene(scene,row):
    """Keep the original fingerprint; version only an explicitly prepared repair."""
    result=copy.deepcopy(scene)
    for stage in ['image','video']:
        revision=row.get('asset_revisions',{}).get(stage,1)
        if revision>1:
            keys=['output_file'] if stage=='image' else ['raw_output_file','silent_output_file']
            for key in keys:
                p=Path(result[stage][key]);result[stage][key]=p.with_stem(p.stem+f'-r{revision:02}').as_posix()
    if row.get('image'):result['video']['source_image_file']=row['image']['file']
    repair=row.get('repair_pending')
    if repair and repair['stage']=='video':
        prompt=('Animate the attached approved still as a single 10-second shot. Preserve its exact full-frame '
                'composition from the first through the last frame, with all four image edges visible. '
                'Fully fixed camera; no zoom, crop, pan, tilt, push-in, orbit, cuts or reframing. '
                'Use only barely perceptible ambient light variation; keep people, vehicles, furniture, '
                'background, windows and every existing object fixed in place. Do not reveal anything '
                'outside the source frame or add, remove or reshape objects, solar panels or people. '
                'Keep the original 2D drawing style. No text, speech, music or sound.')
        result['video']['prompt_en']=prompt;result['video_prompt_en']=prompt
        result['repair_reason']=repair['reason']
    return result

def main(args):
    job=read(safe(args.batch));state=init(job);by_id={s['id']:s for s in job['scenes']}
    if args.command=='init':return {'job_id':job['job_id'],'scenes':len(state['scenes']),'checkpoint':job['checkpoint']['progress']}
    if args.command=='next':
        for s in job['scenes']:
            row=state['scenes'][s['id']]
            if row['running']:return {'action':'resume_existing_job_only','scene_id':s['id'],'running':row['running'],'do_not_resubmit':True}
            if row['status'] in ['failed','blocked','needs_review']:continue
            image_ok=inspect_cached(row,'image');video_ok=inspect_cached(row,'video')
            if image_ok and video_ok:continue
            stage='video' if image_ok else 'image'
            return {'action':'generate_'+stage,'scene':effective_scene(s,row),'approved_source_image':row.get('image')}
        return {'action':'package_batch','statuses':{k:v['status'] for k,v in state['scenes'].items()}}
    if args.command in ['start','record','fail','retry']:
        if args.scene not in by_id:raise ValueError('Scene not in this batch')
        if args.stage not in ['image','video']:raise ValueError('Stage is required')
        original=by_id[args.scene];row=state['scenes'][args.scene]
        policy=job['service_policy']
        if args.command=='retry':
            if row.get('running'):raise ValueError('Unresolved job: recover its result, never retry it')
            if not args.error:raise ValueError('A concrete terminal failure or visual QA reason is required')
            if row['status'] not in ['failed','needs_review']:raise ValueError('Only a terminal failure or rejected asset can be repaired')
            if row['status']=='failed' and row.get('failed_stage')!=args.stage:raise ValueError('Retry the failed stage only')
            asset=row.get(args.stage)
            if row['status']=='needs_review' and (not asset or asset.get('visual_qa',{}).get('ok')):raise ValueError('The selected stage was not rejected by visual QA')
            if asset and asset.get('visual_qa',{}).get('ok'):raise ValueError('An approved asset must be reused')
            attempts=row.setdefault('attempts',{'image':0,'video':0})
            limit=policy.get('max_new_'+args.stage+'_calls_per_scene',1)
            if not 0<attempts[args.stage]<limit:raise ValueError('No bounded repair attempt remains')
            if repair_calls_used()>=policy.get('max_extra_generation_calls_production',0):raise ValueError('Production repair budget exhausted')
            if args.stage=='image' and row.get('video'):raise ValueError('Image repair would invalidate an existing video; separate revision required')
            if args.stage=='video' and (not inspect_cached(row,'image') or not row['image'].get('visual_qa',{}).get('ok')):raise ValueError('Keep and use an approved source image for video repair')
            if asset:inspect_cached(row,args.stage)
            row.setdefault('asset_history',[]).append({'stage':args.stage,'attempt':attempts[args.stage],'asset':copy.deepcopy(asset),'status':row['status'],'error':row.get('error'),'repair_reason':args.error})
            row[args.stage]=None
            row.setdefault('asset_revisions',{})[args.stage]=attempts[args.stage]+1
            row['repair_pending']={'stage':args.stage,'reason':args.error}
            row['status']='pending'
            log(job,state,{'event':'repair_prepared','scene':args.scene,'stage':args.stage,'reason':args.error})
            return {'action':'repair_prepared','scene':effective_scene(original,row),'approved_source_image':row.get('image')}
        s=effective_scene(original,row)
        if args.command=='start':
            if row.get(args.stage) and inspect_cached(row,args.stage):return {'action':'reuse_saved_asset','asset':row[args.stage]}
            if row['running']:
                if row['running']['stage']!=args.stage:raise ValueError('Another stage already has an unresolved job')
                if row['running'].get('job_id') and row['running'].get('job_id')!=args.job_id:raise ValueError('Uncertain existing generation; recover its job ID instead of submitting again')
            else:
                if any(r.get('running') for p in safe('outputs').glob('B*/progress.json') for r in read(p)['scenes'].values()):raise ValueError('Another scene has an unresolved generation job')
                if row['status'] in ['failed','blocked','needs_review']:raise ValueError('Prepare a bounded retry for a terminal failure/rejection first')
                if args.stage=='video' and (not inspect_cached(row,'image') or not row['image'].get('visual_qa',{}).get('ok')):raise ValueError('Video requires an approved source image')
                attempts=row.setdefault('attempts',{'image':0,'video':0})
                limit=policy.get('max_new_'+args.stage+'_calls_per_scene',1)
                if attempts[args.stage]>=limit:raise ValueError('Bounded stage attempt limit exhausted; preserve output and report this ID')
                if attempts[args.stage]>=1:
                    if row.get('repair_pending',{}).get('stage')!=args.stage:raise ValueError('Prepare a bounded retry before another generation')
                    if repair_calls_used()>=policy.get('max_extra_generation_calls_production',0):raise ValueError('Production repair budget exhausted')
                attempts[args.stage]+=1
            row['status']=args.stage+'_running';row['running']={'stage':args.stage,'job_id':args.job_id,'submitted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            log(job,state,{'event':'generation_started','scene':args.scene,'stage':args.stage,'job_id':args.job_id});return row
        if args.command=='fail':
            if row.get('running') and row['running']['stage']!=args.stage:raise ValueError('Failure stage differs from the running job')
            if not args.error:raise ValueError('Report the actual terminal error; uncertain jobs must stay running')
            row['status']='blocked' if args.global_blocker else 'failed';row['failed_stage']=args.stage;row['error']=args.error;row['running']=None
            log(job,state,{'event':'failed','scene':args.scene,'stage':args.stage,'error':args.error});return row
        asset=safe(args.file)
        if row.get(args.stage):
            inspect_cached(row,args.stage)
            if digest(asset)!=row[args.stage]['sha256']:raise ValueError('Recorded asset already exists; use an explicit versioned repair')
            return {'action':'reuse_saved_asset','asset':row[args.stage]}
        if not asset.is_file() or asset.stat().st_size<1024:raise ValueError('No real saved asset')
        qa=read(safe(args.qa)) if args.qa else {'ok':False,'reason':'Visual QA not yet recorded'}
        warnings=[];technical={}
        if args.stage=='image':
            from PIL import Image
            with Image.open(asset) as im:
                im.verify()
            with Image.open(asset) as im:width,height=im.size
            technical={'width':width,'height':height}
            if width<1024 or abs(width/height-16/9)>.02:warnings.append('Image does not meet requested landscape resolution/aspect ratio')
        else:
            if not inspect_cached(row,'image'):raise ValueError('A verified source still is required before recording video')
            raw=safe(s['video']['raw_output_file']);raw.parent.mkdir(parents=True,exist_ok=True)
            if asset!=raw:
                import shutil
                shutil.copyfile(asset,raw)
            silent=safe(s['video']['silent_output_file']);silent.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-map','0:v:0','-c:v','copy','-an',str(silent)],check=True)
            data=probe(silent);v=next(x for x in data['streams'] if x['codec_type']=='video')
            duration=float(data['format']['duration']);technical={'duration_seconds':duration,'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'silent':not any(x['codec_type']=='audio' for x in data['streams']),'raw_file':raw.relative_to(ROOT).as_posix(),'raw_sha256':digest(raw)}
            if not 9.5<=duration<=10.5:warnings.append('Video duration differs from the requested ten seconds')
            if abs(v['width']/v['height']-16/9)>.002:warnings.append('Native video aspect ratio is near, not exact 16:9; local Remotion must fit it')
            if not technical['silent']:raise ValueError('Silent derivative still contains audio')
            asset=silent
            contact=safe(f"outputs/{job['batch_id']}/contact_sheets");contact.mkdir(parents=True,exist_ok=True)
            contact_id=silent.stem
            from PIL import Image,ImageDraw
            sheet=Image.new('RGB',(1440,294),'#182431');draw=ImageDraw.Draw(sheet)
            for i,t in enumerate([0,5,9.5]):
                frame=contact/f'{contact_id}-{i}.jpg';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(min(t,max(0,duration-.1))),'-i',str(silent),'-frames:v','1','-vf','scale=480:270','-q:v','2','-y',str(frame)],check=True)
                with Image.open(frame) as im:sheet.paste(im,(i*480,24))
                draw.text((i*480+8,5),f'{args.scene} | {t}s',fill='white')
            sheet.save(contact/f'{contact_id}.jpg',quality=92)
        row[args.stage]={'file':asset.relative_to(ROOT).as_posix(),'sha256':digest(asset),'bytes':asset.stat().st_size,'technical':technical,'visual_qa':qa,'warnings':warnings}
        row['running']=None;row['status']='needs_review' if not qa.get('ok') else args.stage+'_ready'
        if row.get('repair_pending',{}).get('stage')==args.stage:row.pop('repair_pending')
        log(job,state,{'event':'asset_saved','scene':args.scene,'stage':args.stage,'file':row[args.stage]['file'],'sha256':row[args.stage]['sha256'],'status':row['status']});return row
    if args.command=='package':
        for row in state['scenes'].values():
            for stage in ['image','video']:
                if row.get(stage):inspect_cached(row,stage)
        results={'job_id':job['job_id'],'scenes':state['scenes'],'completed_ids':[k for k,v in state['scenes'].items() if v.get('video') and v['status']=='video_ready'],'pending_ids':[k for k,v in state['scenes'].items() if v['status']=='pending'],'running_ids':[k for k,v in state['scenes'].items() if v['running']],'needs_review_ids':[k for k,v in state['scenes'].items() if v['status']=='needs_review'],'failed_ids':[k for k,v in state['scenes'].items() if v['status']=='failed'],'blocked_ids':[k for k,v in state['scenes'].items() if v['status']=='blocked']}
        write(safe(job['checkpoint']['results']),results)
        folder=safe(f"outputs/{job['batch_id']}")
        files={safe(job['checkpoint'][name]) for name in ['progress','results','journal'] if safe(job['checkpoint'][name]).exists()}
        for sid,row in state['scenes'].items():
            for old in row.get('asset_history',[]):
                data=old.get('asset')
                if data:
                    p=safe(data['file'])
                    if not p.is_file() or digest(p)!=data['sha256']:raise ValueError('Preserved repair history asset missing or changed')
                    files.add(p)
                    if old['stage']=='video':
                        raw=safe(data['technical']['raw_file'])
                        if digest(raw)!=data['technical']['raw_sha256']:raise ValueError('Preserved raw history changed')
                        files.add(raw)
            for stage in ['image','video']:
                if row.get(stage):files.add(safe(row[stage]['file']))
            if row.get('video'):
                files.add(safe(row['video']['technical']['raw_file']))
            if row.get('video') or any(x.get('stage')=='video' and x.get('asset') for x in row.get('asset_history',[])):
                contact=safe(f"outputs/{job['batch_id']}/contact_sheets")
                files.update(p for p in contact.glob(sid+'*.jpg') if p.is_file())
        files=sorted(files)
        write(folder/'checksums.json',{p.relative_to(folder).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files})
        files.append(folder/'checksums.json');groups=[];group=[];size=0;limit=job['delivery']['max_archive_bytes']
        for p in files:
            if group and size+p.stat().st_size+1024>limit:groups.append(group);group=[];size=0
            group.append(p);size+=p.stat().st_size+1024
        if group:groups.append(group)
        deliveries=[]
        for i,group in enumerate(groups,1):
            dest=safe(f"deliveries/{job['batch_id']}-part{i:02}.zip");dest.parent.mkdir(parents=True,exist_ok=True)
            with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
                for p in group:z.write(p,p.relative_to(folder).as_posix())
            deliveries.append({'file':dest.relative_to(ROOT).as_posix(),'bytes':dest.stat().st_size,'sha256':digest(dest)})
        result={'batch_id':job['batch_id'],'archives':deliveries,'independent_zip_archives':True,'results':results}
        write(safe(f"deliveries/{job['batch_id']}-delivery.json"),result)
        master_path=safe('state/master-progress.json')
        seed=safe('state/master-progress.seed.json')
        master=read(master_path) if master_path.exists() else read(seed) if seed.exists() else {'production_id':'rv-ice-full-v6','batches':{}}
        status='complete' if len(results['completed_ids'])==len(job['scenes']) else 'partial'
        master['batches'][job['batch_id']]={'status':status,'completed_ids':results['completed_ids'],'pending_ids':results['pending_ids'],'needs_review_ids':results['needs_review_ids'],'failed_ids':results['failed_ids'],'blocked_ids':results['blocked_ids'],'running_ids':results['running_ids'],'delivery':f"deliveries/{job['batch_id']}-delivery.json"}
        master['updated_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(master_path,master)
        return result
    raise ValueError('Unknown command')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['init','next','start','record','fail','retry','package']);parser.add_argument('--batch',required=True);parser.add_argument('--scene');parser.add_argument('--stage',choices=['image','video']);parser.add_argument('--job-id');parser.add_argument('--file');parser.add_argument('--qa');parser.add_argument('--error');parser.add_argument('--global-blocker',action='store_true')
    try:print(json.dumps(main(parser.parse_args()),ensure_ascii=False,indent=2))
    except Exception as e:raise SystemExit(f'Checkpoint action stopped: {e}')
