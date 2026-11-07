#!/usr/bin/env python3
"""Run one owned build process group, retaining at least6GiB free disk."""
import argparse,json,os,shutil,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cwd',required=True);p.add_argument('--log',required=True)
p.add_argument('--result',required=True);p.add_argument('--floor-gib',type=float,default=6)
p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
command=a.command[1:] if a.command[:1]==['--'] else a.command
if not command:p.error('missing command')
floor=int(a.floor_gib*1024**3);before=shutil.disk_usage(a.cwd).free
result=dict(command=command,cwd=str(Path(a.cwd).resolve()),floor_bytes=floor,before_free_bytes=before)
log=Path(a.log);log.parent.mkdir(parents=True,exist_ok=True)
target=Path(a.result);target.parent.mkdir(parents=True,exist_ok=True)
if before<floor:
 result.update(status='refused-low-disk',exit_code=2);target.write_text(json.dumps(result,indent=2)+'\n');raise SystemExit(2)
started=time.monotonic();low=None
with log.open('w') as output:
 process=subprocess.Popen(command,cwd=a.cwd,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
 result['owned_process_group']=process.pid;last=0
 while process.poll() is None:
  free=shutil.disk_usage(a.cwd).free
  if free<floor:
   low=free;os.killpg(process.pid,signal.SIGTERM)
   try:process.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
   break
  if time.monotonic()-last>=30:
   print(f'Owned build{process.pid}:free{free/1024**3:.2f}GiB;elapsed{time.monotonic()-started:.0f}s',flush=True);last=time.monotonic()
  time.sleep(1)
 result.update(status='stopped-low-disk' if low is not None else 'finished',exit_code=process.wait(),
               elapsed_seconds=time.monotonic()-started,after_free_bytes=shutil.disk_usage(a.cwd).free)
 if low is not None:result['crossed_floor_free_bytes']=low
target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
raise SystemExit(2 if low is not None else result['exit_code'])
