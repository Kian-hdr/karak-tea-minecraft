#!/usr/bin/env python3
"""Build editable block structures and a deterministic Horizon content archive."""
from pathlib import Path
import gzip
import io
import json
import zipfile
import nbtlib as n

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'pack'

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

def offer():
    return {'buy':{'id':'minecraft:emerald','count':1},
            'sell':{'id':'karak_house:karak_tea','count':1},
            'maxUses':16,'uses':0,'rewardExp':True,'xp':1,'priceMultiplier':0.0}

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
    def jig(self,x,y,z,front,name,pool,target):
        self.put(x,y,z,'jigsaw',{'orientation':front+'_up'},
            {'id':'minecraft:jigsaw','name':name,'pool':pool,'target':target,
             'joint':'aligned','final_state':'minecraft:smooth_stone'})
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
    'plains': dict(width=13,depth=14,wood='dark_oak',wall='gray_terracotta',floor='polished_andesite',trim='polished_deepslate',glass='gray_stained_glass',path='stone_bricks',leaves='oak_leaves'),
    'desert': dict(width=15,depth=13,wood='dark_oak',wall='smooth_sandstone',floor='cut_sandstone',trim='brown_terracotta',glass='black_stained_glass',path='smooth_sandstone',leaves='flowering_azalea_leaves'),
    'savanna': dict(width=13,depth=15,wood='acacia',wall='terracotta',floor='smooth_stone',trim='deepslate_tiles',glass='brown_stained_glass',path='granite',leaves='azalea_leaves'),
    'taiga': dict(width=13,depth=14,wood='spruce',wall='cobblestone',floor='polished_andesite',trim='deepslate_bricks',glass='glass',path='cobblestone',leaves='spruce_leaves'),
    'snowy': dict(width=13,depth=14,wood='dark_oak',wall='calcite',floor='smooth_stone',trim='polished_deepslate',glass='light_gray_stained_glass',path='stone_bricks',leaves='spruce_leaves'),
}

def structures():
    for style,t in THEMES.items():
        w,d,wood=t['width'],t['depth'],t['wood'];mid=w//2
        s=Structure((w,11,d))
        s.box((0,0,0),(w-1,10,d-1),'air')
        # Continuous road-to-door paving, with a clearly open 3-block center aisle.
        s.box((0,0,0),(w-1,0,d-1),t['floor'])
        s.box((mid-1,0,0),(mid+1,0,5),t['path'])
        # Deep enclosed volume and tall asymmetrical entrance tower.
        s.box((0,1,5),(w-1,7,d-1),t['wall'])
        s.box((1,1,6),(w-2,6,d-2),'air')
        s.box((0,1,4),(3,8,5),wood+'_planks')
        s.box((1,2,4),(3,7,4),'black_terracotta')
        # Dark vertical fins break up the tall glazing; the inset doorway is central.
        s.box((4,1,5),(w-2,6,5),t['glass'])
        for x in [4,w-2]:s.box((x,1,5),(x,7,5),t['trim'])
        s.box((4,4,5),(w-2,4,5),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        s.box((mid,1,5),(mid+1,3,5),'air')
        for x,hinge in [(mid,'left'),(mid+1,'right')]:
            for y,half in [(1,'lower'),(2,'upper')]:s.put(x,y,5,wood+'_door',{'facing':'north','half':half,'hinge':hinge,'open':'false','powered':'false'})
        s.box((mid,3,5),(mid+1,3,5),'glass')
        # Side window band: the terrace feels connected to a real occupied interior.
        s.box((w-1,2,7),(w-1,5,d-3),t['glass'])
        s.box((0,8,4),(w-1,8,d-1),t['trim'])
        s.box((0,7,3),(w-1,7,4),t['trim'])
        s.box((0,8,3),(w-1,8,3),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        # A warm concealed light line under the canopy.
        for x in range(4,w-1,3):s.put(x,6,4,'lantern',{'hanging':'true','waterlogged':'false'})
        # Slatted pergola over the side patio, kept away from the center walkway.
        for z in [1,3]:s.box((0,5,z),(3,5,z),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        
        for z in [1,3]:s.box((0,1,z),(0,4,z),wood+'_fence',{'east':'false','west':'false','north':'false','south':'false','waterlogged':'false'})
        # Planter boxes and flowers around, never across, the approach.
        for x in [0,w-1]:
            s.box((x,1,0),(x,1,2),'barrel',{'facing':'up','open':'false'})
            s.box((x,2,0),(x,2,2),t['leaves'],{'persistent':'true','distance':'1','waterlogged':'false'})
        for x in [2,w-3]:
            s.put(x,1,2,wood+'_fence',{'east':'false','west':'false','north':'false','south':'false','waterlogged':'false'})
            s.put(x,2,2,wood+'_pressure_plate',{'powered':'false'})
            for z,facing in [(1,'south'),(3,'north')]:s.put(x,1,z,wood+'_stairs',{'facing':facing,'half':'bottom','shape':'straight','waterlogged':'false'})
        # Rich interior: patterned floor, banquette, a service counter and tea shelves.
        s.box((1,0,6),(w-2,0,d-2),wood+'_planks')
        for x in range(2,w-2,2):s.box((x,0,6),(x,0,d-3),t['floor'])
        s.box((1,1,7),(1,1,d-5),wood+'_stairs',{'facing':'east','half':'bottom','shape':'straight','waterlogged':'false'})
        s.box((2,1,d-4),(w-2,1,d-4),wood+'_planks')
        s.put(mid,1,d-4,'lectern',{'facing':'north','has_book':'false','powered':'false'})
        # The seller is enclosed behind a counter screen with an accessible trading hatch.
        s.box((2,2,d-4),(w-2,2,d-4),wood+'_fence',{'east':'true','west':'true','north':'false','south':'false','waterlogged':'false'})
        s.put(mid,2,d-4,'air')
        s.box((2,1,d-2),(w-2,1,d-2),wood+'_planks')
        s.box((2,4,d-2),(w-2,4,d-2),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        for x in range(2,w-2,2):s.put(x,2,d-2,'flower_pot')
        for x in [3,w-4]:s.put(x,6,d-4,'lantern',{'hanging':'true','waterlogged':'false'})
        s.put(2,1,6,'potted_fern')
        # Roof and local identity remain related to the modern Dubai reference.
        if style=='snowy':
            for inset in range(3):
                s.box((inset,8+inset,5),(w-1-inset,8+inset,d-1),wood+'_planks')
                for x,facing in [(inset,'east'),(w-1-inset,'west')]:
                    s.box((x,8+inset,5),(x,8+inset,d-1),wood+'_stairs',{'facing':facing,'half':'bottom','shape':'straight','waterlogged':'false'})
        elif style=='desert':
            s.box((1,9,5),(3,9,d-2),'cut_sandstone_slab',{'type':'bottom','waterlogged':'false'})
            for z in range(6,d-1,2):s.put(0,9,z,'sandstone_wall',{'east':'none','west':'none','north':'none','south':'none','up':'true','waterlogged':'false'})
        elif style=='savanna':
            s.box((w-2,8,1),(w-1,8,5),wood+'_slab',{'type':'bottom','waterlogged':'false'})
        # Large type rendered by the game's text display, with no raster logo.
        def label(pos,text,scale):
            tag={'id':'minecraft:text_display','Pos':list(pos),'Rotation':[n.Float(180.0),n.Float(0.0)],'text':text,
                 'background':0,'brightness':{'block':15,'sky':15},'billboard':'fixed','alignment':'center','line_width':180,
                 'text_opacity':n.Byte(-1),'shadow':False,
                 'transformation':{'translation':[n.Float(0.0),n.Float(0.0),n.Float(0.0)],'scale':[n.Float(scale),n.Float(scale),n.Float(scale)],
                 'left_rotation':[n.Float(0),n.Float(0),n.Float(0),n.Float(1)],'right_rotation':[n.Float(0),n.Float(0),n.Float(0),n.Float(1)]}}
            # nbt.Byte is already typed; compound() preserves it.
            s.entities.append({'pos':list(pos),'blockPos':[int(v) for v in pos],'nbt':tag})
        label((2.0,6.0,3.94),'KARAK\nHOUSE',3.6)
        s.sign(2,2,3,['KARAK TEA','1 Emerald','5-minute powers','Ask for free tea'])
        s.jig(mid,0,0,'north','minecraft:building_entrance','minecraft:empty','minecraft:building_entrance')
        seller={'id':'minecraft:villager','Pos':[mid+0.5,1.0,d-2.5],
            'Rotation':[n.Float(180.0),n.Float(0.0)],'Tags':['karak_seller'],'CustomName':'Karak Seller',
            'CustomNameVisible':True,'PersistenceRequired':True,
            'VillagerData':{'profession':'minecraft:librarian','level':2,'type':'minecraft:'+('snow' if style=='snowy' else style)},
            'Xp':10,'Offers':{'Recipes':[offer()]}}
        s.entities.append({'pos':seller['Pos'],'blockPos':[mid,1,d-3],'nbt':seller})
        s.save('karak_house_'+style)

def pools():
    for style in THEMES:
        single={'element_type':'minecraft:single_pool_element','location':'karak_house:village/karak_house_'+style,
                'processors':{'processors':[]},'projection':'rigid'}
        gate={'element_type':'lithostitched:guaranteed','count':1,'min_depth':0,'delegate':single}
        write(f'data/karak_house/worldgen/template_pool/additions/{style}.json',
            {'horizon:add_to':f'minecraft:village/{style}/houses','elements':[{'weight':1,'element':gate}]})

def functions():
    write('data/karak_house/function/load.mcfunction',
        'scoreboard objectives add karak_day dummy\nscoreboard objectives add karak_free dummy\nscoreboard objectives add karak_sys dummy\nscoreboard objectives add karak_talk minecraft.custom:minecraft.talked_to_villager\n')
    write('data/karak_house/function/tick.mcfunction',
        'execute store result score #today karak_sys run time of minecraft:overworld query day repetition\n'
        'execute as @e[type=minecraft:villager,tag=karak_seller] unless score @s karak_day matches 0.. run scoreboard players set @s karak_day -1\n'
        'execute as @e[type=minecraft:villager,tag=karak_seller] if score @s karak_day < #today karak_sys run function karak_house:new_day\n'
        'execute as @a[scores={karak_talk=1..}] at @s if predicate karak_house:looking_at_seller run function karak_house:interact\n'
        'scoreboard players set @a[scores={karak_talk=1..}] karak_talk 0\n')
    write('data/karak_house/function/new_day.mcfunction',
        'scoreboard players operation @s karak_day = #today karak_sys\n'
        'execute store result score @s karak_free run random value 1..10\n'
        'execute unless score @s karak_free matches 1 run scoreboard players set @s karak_free 0\n'
        'data merge entity @s {CustomName:"Karak Seller"}\n'
        'execute if score @s karak_free matches 1 run data merge entity @s {CustomName:"Karak Seller - Free Tea!"}\n')
    write('data/karak_house/predicate/looking_at_seller.json', {
        'type':'minecraft:entity_properties','entity':'this',
        'predicate':{'minecraft:type_specific/player':{'looking_at':{
            'minecraft:entity_type':'minecraft:villager','minecraft:nbt':'{Tags:["karak_seller"]}'}}}})
    write('data/karak_house/advancement/entity_context.json', {'criteria':{'context':{'trigger':'minecraft:impossible','conditions':{'player':[{'type':'minecraft:entity_properties','entity':'this','predicate':{'minecraft:nbt':'{Tags:["karak_seller"]}'}}]}}}})
    write('data/karak_house/function/interact.mcfunction',
        'tag @s add karak_customer\n'
        'execute at @s as @e[type=minecraft:villager,tag=karak_seller,distance=..6,sort=nearest,limit=1] if score @s karak_free matches 1 run function karak_house:giveaway\n'
        'tag @s remove karak_customer\n')
    write('data/karak_house/function/giveaway.mcfunction',
        'scoreboard players set @s karak_free 0\n'
        'data merge entity @s {CustomName:"Karak Seller"}\n'
        'give @a[tag=karak_customer,limit=1] karak_house:karak_tea 1\n'
        'tellraw @a[tag=karak_customer,limit=1] {"text":"This Karak Tea is on the house!","color":"gold"}\n')

def cup():
    # Editable cuboids reference vanilla textures, not generated image files.
    elements=[]
    def box(a,b,texture):
        elements.append({'from':a,'to':b,'faces':{face:{'texture':'#'+texture} for face in ['north','south','east','west','up','down']}})
    box([4,1,4],[12,2,12],'cup');box([4,2,4],[5,11,12],'cup');box([11,2,4],[12,11,12],'cup')
    box([5,2,4],[11,11,5],'cup');box([5,2,11],[11,11,12],'cup');box([5,9,5],[11,10,11],'tea')
    box([12,4,6],[14,5,10],'cup');box([13,5,6],[14,9,10],'cup');box([12,9,6],[14,10,10],'cup')
    write('assets/karak_house/models/item/karak_tea.json',{'parent':'minecraft:block/block','textures':{
        'cup':'minecraft:block/smooth_quartz','tea':'minecraft:block/brown_terracotta','particle':'minecraft:block/brown_terracotta'},
        'elements':elements,'display':{'gui':{'rotation':[25,225,0],'translation':[0,-1,0],'scale':[0.9,0.9,0.9]},
        'firstperson_righthand':{'rotation':[0,-40,0],'translation':[0,2,0],'scale':[0.65,0.65,0.65]},
        'thirdperson_righthand':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[0.55,0.55,0.55]}}})

def build():
    structures();pools();functions();cup()
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    file=out/'Karak_Tea_0.1.0.hmod'
    with zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PACK.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(PACK).as_posix(),(2026,11,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(info,p.read_bytes())
    print(file)
if __name__=='__main__':build()
