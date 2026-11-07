#!/usr/bin/env python3
"""Create the supported source-only .hnmod layout; never installs/publishes it."""
from pathlib import Path
import argparse,hashlib,json,re,zipfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args()
text=(root/'horizon-mixin.toml').read_text();section=text.split('[compatibility]')[0]
ident=re.search(r'^id = "([a-z0-9_]+)"$',section,re.M).group(1)
version=re.search(r'^version = "([^"]+)"$',section,re.M).group(1)
metadata=dict(schema=1,id=ident,version=version,game='26.3',
 horizon='66f3981f522b24c250b21523a70080965b940424',
 mixins='e8cd0aa38cffef49cb2e088ef716baa107148c02')
files={f'mixins/{ident}/'+str(x.relative_to(root)):x.read_bytes()
 for x in sorted(root.rglob('*')) if x.is_file() and
 (x.suffix=='.rs' or x.name in ['horizon-mixin.toml','README.md','NOTICE.md'])}
files['horizon-native.json']=(json.dumps(metadata,indent=2)+'\n').encode()
assert len(files)<512 and sum(map(len,files.values()))<64*1024**2
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for name,content in sorted(files.items()):
  info=zipfile.ZipInfo(name,(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o100644<<16;z.writestr(info,content)
print(json.dumps(dict(path=str(out.resolve()),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
 entries=len(files),unpacked_bytes=sum(map(len,files.values())),metadata=metadata),indent=2))
