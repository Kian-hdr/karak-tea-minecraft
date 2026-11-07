#!/usr/bin/env python3
"""Build editable block structures and a deterministic Horizon content archive."""
from pathlib import Path
import gzip
import io
import json
import zipfile
import nbtlib as n
from gameplay import write_gameplay
from stations import seller_nbt, anchor_nbt, write_stations
from cup_model import write_cup_model
from gui_icons import write_gui_icons
from catalog import CATALOG, offer, write_catalog
from powers import write_powers, reconcile_owned_generated
from doors import write_doors
from worldgen import write_worldgen

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'pack'
VERSION = '0.2.0'

def write(path, value):
    p = PACK / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, indent=2)+'\n')

def compound(value):
    if isinstance(value, n.tag.Base): return value
    if isinstance(value, dict): return n.Compound({k:compound(v) for k,v in value.items()})
    if isinstance(value, str): return n.String(value)
    if isinstance(value, bool): return n.Byte(value)
    if isinstance(value, int): return n.Int(value)
    if isinstance(value, float): return n.Double(value)
    if isinstance(value, list):
        tags=[compound(v) for v in value]
        return n.List[type(tags[0]) if tags else n.Compound](tags)
    raise TypeError(value)

class Structure:
    def __init__(self, size): self.size=size; self.blocks={}; self.entities=[]
    def put(self,x,y,z,name,props=None,nbt=None):
        state={'id':'minecraft:'+name}
        if props: state['properties']=props
        self.blocks[x,y,z]=(state,nbt)
    def box(self,a,b,name,props=None):
        for x in range(a[0],b[0]+1):
            for y in range(a[1],b[1]+1):
                for z in range(a[2],b[2]+1):self.put(x,y,z,name,props)
    def jig(self,x,y,z,front,name,pool,target,final_state='smooth_stone'):
        self.put(x,y,z,'jigsaw',{'orientation':front+'_up'},
            {'id':'minecraft:jigsaw','name':name,'pool':pool,'target':target,
             'joint':'aligned','final_state':'minecraft:'+final_state})
    def sign(self,x,y,z,lines,facing='north'):
        self.put(x,y,z,'dark_oak_wall_sign',{'facing':facing,'waterlogged':'false'},
            {'id':'minecraft:sign','is_waxed':True,
             'front_text':{'messages':lines,'color':'white','has_glowing_text':True},
             'back_text':{'messages':['','','',''],'color':'white','has_glowing_text':False}})
    def save(self,name):
        palette=[]; keys={}; blocks=[]
        for pos,(state,tag) in sorted(self.blocks.items()):
            key=json.dumps(state,sort_keys=True)
            if key not in keys:keys[key]=len(palette);palette.append(state)
            b={'pos':list(pos),'state':keys[key]}
            if tag:b['nbt']=tag
            blocks.append(b)
        data={'DataVersion':5023,'size':list(self.size),'palette':palette,'blocks':blocks,'entities':self.entities}
        f=n.File(compound(data)); raw=io.BytesIO();f.write(raw)
        p=PACK/f'data/karak_house/structure/village/{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(gzip.compress(raw.getvalue(),mtime=0))

THEMES = {
    'plains': dict(width=13,depth=12,wood='dark_oak',wall='gray_terracotta',floor='polished_andesite',trim='polished_deepslate',glass='gray_stained_glass',path='stone_bricks',leaves='oak_leaves'),
    'desert': dict(width=15,depth=13,wood='dark_oak',wall='smooth_sandstone',floor='cut_sandstone',trim='brown_terracotta',glass='black_stained_glass',path='smooth_sandstone',leaves='flowering_azalea_leaves'),
    'savanna': dict(width=13,depth=13,wood='acacia',wall='terracotta',floor='smooth_stone',trim='deepslate_tiles',glass='brown_stained_glass',path='polished_granite',leaves='azalea_leaves'),
    'taiga': dict(width=13,depth=13,wood='spruce',wall='cobblestone',floor='polished_andesite',trim='deepslate_bricks',glass='glass',path='cobblestone',leaves='spruce_leaves'),
    'snowy': dict(width=13,depth=13,wood='dark_oak',wall='calcite',floor='smooth_stone',trim='polished_deepslate',glass='light_gray_stained_glass',path='stone_bricks',leaves='spruce_leaves'),
}

def structures():
    for style,t in THEMES.items():
        w,d,wood=t['width'],t['depth'],t['wood'];mid=w//2
        s=Structure((w,11,d))
        s.box((0,0,0),(w-1,10,d-1),'air')
        # Continuous road-to-door paving, with a clearly open 3-block center aisle.
        s.box((0,0,0),(w-1,0,d-1),t['floor'])
        s.box((mid-1,0,0),(mid+1,0,5),t['path'])
        # A raised landing keeps terrain-matching village roads from repainting
        # the walkway. Three inward-facing steps bridge the road without a jump.
        stair = {'stone_bricks':'stone_brick_stairs',
                 'smooth_sandstone':'smooth_sandstone_stairs',
                 'polished_granite':'polished_granite_stairs',
                 'cobblestone':'cobblestone_stairs'}[t['path']]
        s.box((mid-1,0,0),(mid+1,0,0),stair,
              {'facing':'south','half':'bottom','shape':'straight','waterlogged':'false'})
        # Deep enclosed volume and tall asymmetrical entrance tower.
        s.box((0,1,5),(w-1,7,d-1),t['wall'])
        s.box((1,1,6),(w-2,6,d-2),'air')
        s.box((0,1,4),(3,8,5),wood+'_planks')
        s.box((1,2,4),(3,7,4),'black_terracotta')
        # The glazing and closed door surfaces share the front plane, z=5.
        s.box((4,1,5),(w-2,6,5),t['glass'])
        for x in [4,w-2]:s.box((x,1,5),(x,7,5),t['trim'])
        s.box((4,4,5),(w-1,4,5),wood+'_planks')
        s.box((mid,1,5),(mid+1,3,5),'air')
        for x,hinge in [(mid,'right'),(mid+1,'left')]:
            for y,half in [(1,'lower'),(2,'upper')]:s.put(x,y,5,wood+'_door',{'facing':'south','half':half,'hinge':hinge,'open':'false','powered':'false'})
        for px in [mid,mid+1]:
            for pz in [4,6]:
                s.put(px,1,pz,wood+'_pressure_plate',{'powered':'false'})
        s.box((mid,3,5),(mid+1,3,5),t['glass'])
        # Side window band: the terrace feels connected to a real occupied interior.
        s.box((w-1,2,7),(w-1,5,d-3),t['glass'])
        s.box((0,8,4),(w-1,8,d-1),t['trim'])
        s.box((0,7,3),(w-1,7,4),t['trim'])
        s.box((0,8,3),(w-1,8,3),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        # A warm concealed light line under the canopy.
        for x in range(4,w-1,3):s.put(x,6,4,'lantern',{'hanging':'true','waterlogged':'false'})
        # Slatted pergola over the side patio, kept away from the center walkway.
        for z in [1,3]:s.box((w-4,4,z),(w-1,4,z),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        s.box((w-2,4,1),(w-2,4,4),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        
        for z in [1,3]:s.box((w-2,1,z),(w-2,3,z),wood+'_fence',{'east':'false','west':'false','north':'false','south':'false','waterlogged':'false'})
        # Planter boxes and flowers around, never across, the approach.
        for x in [0,w-1]:
            s.box((x,1,0),(x,1,2),'barrel',{'facing':'up','open':'false'})
            s.box((x,2,0),(x,2,2),t['leaves'],{'persistent':'true','distance':'1','waterlogged':'false'})
        for x in [2,w-3]:
            s.put(x,1,2,wood+'_fence',{'east':'false','west':'false','north':'false','south':'false','waterlogged':'false'})
            s.put(x,2,2,wood+'_pressure_plate',{'powered':'false'})
            for z,facing in [(1,'north'),(3,'south')]:s.put(x,1,z,wood+'_stairs',{'facing':facing,'half':'bottom','shape':'straight','waterlogged':'false'})
        # A furnished cafe with a clear central aisle to the service counter.
        s.box((1,0,6),(w-2,0,d-2),wood+'_planks')
        s.box((mid-1,0,6),(mid+1,0,d-4),t['floor'])
        accent={'plains':'brown','desert':'orange','savanna':'red','taiga':'green','snowy':'light_gray'}[style]
        for tx in [3,w-4]:
            s.put(tx,1,7,wood+'_fence',{'east':'false','west':'false','north':'false','south':'false','waterlogged':'false'})
            s.put(tx,2,7,wood+'_pressure_plate',{'powered':'false'})
            for cx,facing in [(tx-1,'west'),(tx+1,'east')]:
                s.put(cx,1,7,wood+'_stairs',{'facing':facing,'half':'bottom','shape':'straight','waterlogged':'false'})
        # Low, open counter: no fence screen across the seller's face.
        s.box((2,1,d-4),(w-2,1,d-4),'smooth_quartz')
        s.put(mid,1,d-4,'lectern',{'facing':'north','has_book':'false','powered':'false'})
        s.box((2,1,d-2),(w-2,1,d-2),wood+'_planks')
        s.box((2,2,d-1),(w-2,4,d-1),t['trim'])
        for xx in [2,w-3]:s.box((xx,2,d-1),(xx,5,d-1),'stripped_'+wood+'_log',{'axis':'y'})
        for yy in [3,5]:
            s.box((2,yy,d-2),(w-3,yy,d-2),wood+'_slab',{'type':'top','waterlogged':'false'})
            for xx in range(3,w-3,2):s.put(xx,yy+1,d-2,'flower_pot')
        s.sign(mid,4,d-2,['KARAK TEA','Warm & spiced','1 Emerald','Made fresh'])
        s.sign(3,4,d-2,['TODAY AT','KARAK HOUSE','','Ask for free tea'])
        # Lower pendant clusters and ceiling beams make the tall room intimate.
        for zz in [7,d-4]:
            s.box((1,6,zz),(w-2,6,zz),wood+'_slab',{'type':'top','waterlogged':'false'})
        for xx in [3,w-4]:
            for yy in [5,6]:s.put(xx,yy,7,'iron_chain',{'axis':'y','waterlogged':'false'})
            s.put(xx,4,7,'lantern',{'hanging':'true','waterlogged':'false'})
        for xx in [2,w-2]:s.put(xx,1,d-5,'potted_fern')
        s.box((1,2,6),(1,4,6),'stripped_'+wood+'_log',{'axis':'y'})
        # Light interior wall finish, framed with timber like the reference cafe.
        interior_wall='smooth_sandstone' if style=='desert' else ('calcite' if style=='snowy' else 'white_terracotta')
        s.box((0,1,6),(0,6,d-2),interior_wall)
        # Framed geometric wall panel and illuminated ledges above the dining area.
        s.box((0,2,6),(0,5,d-5),'stripped_'+wood+'_log',{'axis':'y'})
        s.box((0,3,7),(0,4,d-6),accent+'_terracotta')
        s.put(0,3,7,'white_terracotta')
        for zz in [6]:
            s.put(1,3,zz,wood+'_slab',{'type':'top','waterlogged':'false'})
        s.put(1,4,6,'potted_fern')
        # A compact indoor tree grows from a supported planter between the tables.
        s.put(3,1,8,'barrel',{'facing':'up','open':'false'})
        s.box((3,2,8),(3,4,8),'dark_oak_log',{'axis':'y'})
        for xx in [2,4]:s.put(xx,4,8,'dark_oak_log',{'axis':'x'})
        s.box((2,5,7),(4,5,9),'azalea_leaves',{'persistent':'true','distance':'1','waterlogged':'false'})
        for xx,zz in [(2,7),(2,9),(4,7),(4,9),(3,8)]:
            s.put(xx,4 if xx!=3 else 6,zz,'azalea_leaves',{'persistent':'true','distance':'1','waterlogged':'false'})
        # Finish all exterior elevations after interior decoration, so interior
        # backing blocks cannot leak through as an accidental patchwork outside.
        for side in [0,w-1]:
            s.box((side,1,6),(side,7,d-1),t['wall'])
            s.box((side,1,6),(side,1,d-1),t['trim'])
            s.box((side,7,6),(side,7,d-1),t['trim'])
            for zz in [6,d-2]:
                s.box((side,2,zz),(side,6,zz),'stripped_'+wood+'_log',{'axis':'y'})
            s.box((side,2,7),(side,5,d-3),t['glass'])
            s.box((side,4,7),(side,4,d-3),wood+'_planks')
        s.box((1,1,d-1),(w-2,7,d-1),t['wall'])
        s.box((0,1,d-1),(w-1,1,d-1),t['trim'])
        s.box((0,7,d-1),(w-1,7,d-1),t['trim'])
        s.box((1,2,d-1),(w-2,3,d-1),wood+'_planks')
        s.box((1,4,d-1),(w-2,4,d-1),wood+'_planks')
        for xx in [2,w-3]:
            s.box((xx,2,d-1),(xx,6,d-1),'stripped_'+wood+'_log',{'axis':'y'})
        s.box((3,5,d-1),(w-4,6,d-1),t['glass'])
        # Roof and local identity remain related to the modern Dubai reference.
        if style=='snowy':
            for inset in range(3):
                s.box((inset,8+inset,5),(w-1-inset,8+inset,d-1),wood+'_planks')
                for x,facing in [(inset,'east'),(w-1-inset,'west')]:
                    s.box((x,8+inset,5),(x,8+inset,d-1),wood+'_stairs',{'facing':facing,'half':'bottom','shape':'straight','waterlogged':'false'})
        elif style=='desert':
            s.box((1,9,5),(3,9,d-2),'cut_sandstone_slab',{'type':'bottom','waterlogged':'false'})
            for z in range(6,d-1,2):s.put(0,9,z,'sandstone_wall',{'east':'none','west':'none','north':'none','south':'none','up':'true','waterlogged':'false'})
        # Large type rendered by the game's text display, with no raster logo.
        def label(pos,text,scale):
            tag={'id':'minecraft:text_display','Pos':list(pos),'Rotation':[n.Float(180.0),n.Float(0.0)],'text':text,
                 'background':0,'brightness':{'block':15,'sky':15},'billboard':'fixed','alignment':'center','line_width':180,
                 'text_opacity':n.Byte(-1),'shadow':False,
                 'transformation':{'translation':[n.Float(0.0),n.Float(0.0),n.Float(0.0)],'scale':[n.Float(scale),n.Float(scale),n.Float(scale)],
                 'left_rotation':[n.Float(0),n.Float(0),n.Float(0),n.Float(1)],'right_rotation':[n.Float(0),n.Float(0),n.Float(0),n.Float(1)]}}
            # nbt.Byte is already typed; compound() preserves it.
            s.entities.append({'pos':list(pos),'blockPos':[int(v) for v in pos],'nbt':tag})
        label((2.5,5.6,3.90),'KARAK',3.3)
        label((2.5,4.6,3.90),'HOUSE',3.3)
        s.sign(2,2,3,['KARAK TEA','1 Emerald','5-minute powers','Ask for free tea'])
        s.jig(mid,0,0,'north','minecraft:building_entrance','minecraft:empty','minecraft:building_entrance',
              stair+'[facing=south,half=bottom,shape=straight,waterlogged=false]')
        pos=[mid+0.5,1.0,d-2.5]
        seller=seller_nbt(style,pos)
        seller['Rotation']=[n.Float(180.0),n.Float(0.0)]
        anchor=anchor_nbt(style,pos)
        for entity in [seller,anchor]:
            s.entities.append({'pos':pos,'blockPos':[mid,1,d-3],'nbt':entity})
        s.save('karak_house_'+style)

def build():
    structures();write_worldgen(write,THEMES);write_gameplay(write);write_stations(write);write_doors(write,THEMES)
    emitted = write_powers(write)
    reconcile_owned_generated(PACK, emitted)
    write_catalog(write);write_cup_model(write);write_gui_icons(write)
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    file=out/f'Karak_Tea_{VERSION}.hmod'
    with zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PACK.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(PACK).as_posix(),(2026,11,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(info,p.read_bytes())
    print(file)
if __name__=='__main__':build()
