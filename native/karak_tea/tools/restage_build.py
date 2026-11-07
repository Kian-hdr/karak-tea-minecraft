#!/usr/bin/env python3
"""Apply the official SDK into a fresh stage and compile with the owned disk guard."""
from pathlib import Path
import argparse,os,subprocess,shutil,json,sys
root=Path(__file__).resolve().parents[3];p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--pass-name',required=True);p.add_argument('--rust-bin',required=True);a=p.parse_args()
cache=root/'.build/native_ui';out=root/'evidence/private/native_ui';stage=cache/'stage';old=cache/'stage_previous'
assert a.pass_name.replace('_','').isalnum();assert (stage/'.horizon-mixins-stage.json').is_file() and not old.exists()
env=dict(os.environ);env.update(PATH=a.rust_bin+os.pathsep+env['PATH'],CARGO_HOME=str(cache/'cargo_home'),RUSTC=str(Path(a.rust_bin)/'rustc'),RUSTDOC=str(Path(a.rust_bin)/'rustdoc'))
stage.rename(old)
with (out/f'SDK_Apply_{a.pass_name}.log').open('w') as log:
 subprocess.run([str(cache/'sdk_target/debug/horizon-mixins'),'apply','--workspace',str(cache/'horizon'),'--mods',str(root/'native'),'--out',str(stage)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
changed=[]
for f in stage.rglob('*'):
 previous=old/f.relative_to(stage)
 if f.is_file():
  if previous.is_file() and f.read_bytes()==previous.read_bytes():
   s=previous.stat();os.utime(f,ns=(s.st_atime_ns,s.st_mtime_ns))
  else:changed.append(str(f.relative_to(stage)))
for f in sorted(stage.rglob('*'),reverse=True):
 previous=old/f.relative_to(stage)
 if f.is_dir() and previous.is_dir():
  s=previous.stat();os.utime(f,ns=(s.st_atime_ns,s.st_mtime_ns))
(out/f'Restage_{a.pass_name}.json').write_text(json.dumps(dict(official_sdk_stage=True,changed_files=changed),indent=2)+'\n')
shutil.rmtree(old);print('Official stage ready:',changed,flush=True)
command=[sys.executable,str(root/'native/karak_tea/tools/build_guard.py'),'--cwd',str(stage),'--log',str(out/f'Native_Build_{a.pass_name}.log'),'--result',str(out/f'Native_Build_{a.pass_name}.json'),'--',str(Path(a.rust_bin)/'cargo'),'build','--locked','-p','horizon-client','--bin','horizon-client','--profile','fast','-j2','--target-dir',str(cache/'target'),'--config','profile.fast.debug=0','--config','profile.fast.incremental=false','--config','profile.fast.lto=false','--config','profile.fast.package.horizon-client.opt-level=0']
raise SystemExit(subprocess.run(command,env=env).returncode)
