#!/usr/bin/env python3
"""Render private design-review dioramas in an isolated Horizon test instance."""
import json, os, subprocess, time
from pathlib import Path
from build import THEMES
ROOT=Path(__file__).resolve().parents[1]
CTL=os.environ['HORIZON_CTL']; SOCKET=os.environ.get('KARAK_SOCKET','/tmp/karak-tea.sock')
OUT=ROOT/'evidence'/'Design_Review';OUT.mkdir(parents=True,exist_ok=True)
def ctl(*args):
 p=subprocess.run([CTL,'--socket',SOCKET,*map(str,args)],capture_output=True,text=True,timeout=65)
 r=json.loads(p.stdout)
 if 'error' in r:raise RuntimeError(r)
 return r
def cmd(s):
 r=ctl('command',s)
 if any(t in ' '.join(r.get('chat',[])).lower() for t in ['not loaded','too many blocks','failed to','unknown or incomplete','incorrect argument']):raise RuntimeError((s,r))
 return r
def wait():ctl('wait',4)
cmd('gamemode spectator');cmd('effect clear @s');cmd('weather clear');cmd('time set 6000');cmd('time pause')
ctl('options-set','fov','55');ctl('options-set','renderDistance','4');ctl('options-set','guiScale','3')
styles=[('plains',13,12,'grass_block','dirt_path'),('desert',15,13,'sand','smooth_sandstone'),('savanna',13,13,'red_sand','granite'),('taiga',13,13,'podzol','cobblestone'),('snowy',13,13,'snow_block','stone_bricks')]
for i,(style,w,d,ground,road) in enumerate(styles):
 x=100+i*120;z=150;y=80
 cmd(f'tp @s {x+w/2} {y+10} {z-12}');ctl('wait',20);ctl('wait-ready',45)
 cmd('kill @e[type=minecraft:villager,distance=..32]');cmd('kill @e[type=minecraft:text_display,distance=..32]')
 cmd(f'fill {x-16} {y-8} {z-22} {x+w+16} {y-1} {z+d+16} dirt')
 cmd(f'fill {x-16} {y-1} {z-22} {x+w+16} {y-1} {z+d+16} {ground}')
 cmd(f'fill {x-16} {y} {z-22} {x+w+16} {y+10} {z+d+16} air')
 cmd(f'fill {x-16} {y-1} {z-4} {x+w+16} {y-1} {z-1} {road}')
 cmd(f'place template karak_house:village/karak_house_{style} {x} {y-1} {z}')
 paving={'plains':'stone_bricks','desert':'smooth_sandstone','savanna':'granite','taiga':'cobblestone','snowy':'stone_bricks'}[style]
 cmd(f'setblock {x+w//2} {y-1} {z} {paving}')
 cmd(f'setblock {x+w//2} {y} {z} air')
 wait()
 # Clean architectural reference views, rendered by the actual target game.
 cmd(f'tp @s {x+w+3} {y+4} {z-5}')
 ctl('look-at',x+w/2,y+3,z+6);wait()
 ctl('screenshot',str(OUT/f'{style}_exterior.png'))
 cmd(f'tp @s {x+w/2} {y+1} {z-6}')
 ctl('look-at',x+w/2,y+1.5,z+6);wait()
 ctl('screenshot',str(OUT/f'{style}_entrance.png'))
 for opened in [True,False]:
  for dx,hinge in [(w//2,'right'),(w//2+1,'left')]:
   for dy,half in [(0,'lower'),(1,'upper')]:
    cmd(f'setblock {x+dx} {y+dy} {z+5} {THEMES[style]["wood"]}_door[facing=south,half={half},hinge={hinge},open={str(opened).lower()},powered=false]')
  wait()
  if opened:ctl('screenshot',str(OUT/f'{style}_doors_open.png'))
 cmd(f'tp @s {x+w-2} {y+2} {z+d-3}')
 ctl('look-at',x+3,y+1.3,z+7.5);wait()
 ctl('screenshot',str(OUT/f'{style}_interior.png'))
 ctl('options-set','fov','70')
 cmd(f'tp @s {x+w/2} {y+3} {z+d-2}')
 ctl('look-at',x+w/2,y+1,z+6);wait()
 ctl('screenshot',str(OUT/f'{style}_seating.png'))
 ctl('options-set','fov','55')
 print(style, 'rendered', flush=True)
print(OUT)
