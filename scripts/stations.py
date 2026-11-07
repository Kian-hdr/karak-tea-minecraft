"""Persistent, content-only Karak stations and replaceable resilient sellers."""
import json
from catalog import CATALOG, offer

STYLES=('plains','desert','savanna','taiga','snowy')

def seller_nbt(style, pos):
    return {'id':'minecraft:villager','Pos':list(pos),'Tags':['karak_seller','karak_catalog_020_six',f'karak_style_{style}'],
            'CustomName':'Karak Seller','CustomNameVisible':True,'PersistenceRequired':True,
            'Health':200.0,'attributes':[{'id':'minecraft:max_health','base':200.0},{'id':'minecraft:movement_speed','base':0.0}],
            'VillagerData':{'profession':'minecraft:none','level':2,'type':'minecraft:plains'},
            'Xp':10,'Offers':{'Recipes':[offer(item) for item,_,_ in CATALOG]}}

def anchor_nbt(style,pos):
    return {'id':'minecraft:marker','Pos':list(pos),'Tags':['karak_anchor',f'karak_style_{style}'],'Rotation':[180.0,0.0]}

def snbt(value):
    # JSON's quoted keys/strings and decimal numbers are valid SNBT here.
    return json.dumps(value,separators=(',',':'))

def write_stations(write):
    def fn(name,lines):write(f'data/karak_house/function/stations/{name}.mcfunction',lines)
    fn('load','scoreboard objectives add karak_sid dummy\nscoreboard objectives add karak_wait dummy\nexecute unless score #next_station karak_sys matches 0.. run scoreboard players set #next_station karak_sys 0\n')
    fn('harden','attribute @s minecraft:max_health base set 200\nattribute @s minecraft:movement_speed base set 0\nattribute @s minecraft:jump_strength base set 0\nattribute @s minecraft:armor base set 12\nattribute @s minecraft:knockback_resistance base set 1\n')
    fn('tick','execute as @e[type=minecraft:marker,tag=karak_anchor] at @s run function karak_house:stations/check\n')
    fn('init','scoreboard players add #next_station karak_sys 1\nscoreboard players operation @s karak_sid = #next_station karak_sys\nscoreboard players set @s karak_wait 0\nscoreboard players set @s karak_day -1\nscoreboard players set @s karak_free 0\nscoreboard players operation #station karak_sys = @s karak_sid\nexecute as @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] unless score @s karak_sid matches 1.. run scoreboard players operation @s karak_sid = #station karak_sys\nscoreboard players operation @s karak_day = @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] karak_day\nscoreboard players operation @s karak_free = @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] karak_free\n')
    fn('check','execute unless score @s karak_sid matches 1.. run function karak_house:stations/init\nscoreboard players operation #station karak_sys = @s karak_sid\ntag @e[tag=karak_station_vendor] remove karak_station_vendor\nexecute as @e[type=minecraft:villager,tag=karak_seller,nbt=!{Health:0.0f}] if score @s karak_sid = #station karak_sys run tag @s add karak_station_vendor\nexecute if entity @e[tag=karak_station_vendor] run function karak_house:stations/snapshot\nexecute unless entity @e[tag=karak_station_vendor] run scoreboard players add @s karak_wait 1\nexecute if score @s karak_wait matches 100.. run function karak_house:stations/respawn\ntag @e[tag=karak_station_vendor] remove karak_station_vendor\n')
    fn('snapshot','scoreboard players set @s karak_wait 0\nscoreboard players operation @s karak_day = @e[tag=karak_station_vendor,limit=1] karak_day\nscoreboard players operation @s karak_free = @e[tag=karak_station_vendor,limit=1] karak_free\n')
    fn('commit_claim','execute unless score @e[tag=karak_target,limit=1] karak_sid matches 1.. run return 0\nscoreboard players operation #claimed_station karak_sys = @e[tag=karak_target,limit=1] karak_sid\nexecute as @e[type=minecraft:marker,tag=karak_anchor] if score @s karak_sid = #claimed_station karak_sys run scoreboard players set @s karak_free 0\n')
    lines='scoreboard players operation #saved_day karak_sys = @s karak_day\nscoreboard players operation #saved_free karak_sys = @s karak_free\n'
    for style in STYLES:lines+=f'execute if entity @s[tag=karak_style_{style}] run function karak_house:stations/spawn_{style}\n'
    lines+='execute as @e[tag=karak_new_vendor,distance=..1,limit=1] run function karak_house:stations/restore\nscoreboard players set @s karak_wait 0\n'
    fn('respawn',lines)
    fn('restore','tp @s ~ ~ ~ ~ ~\nscoreboard players operation @s karak_sid = #station karak_sys\nscoreboard players operation @s karak_day = #saved_day karak_sys\nscoreboard players operation @s karak_free = #saved_free karak_sys\nfunction karak_house:stations/harden\nexecute if score @s karak_free matches 1 run data merge entity @s {CustomName:"Karak Seller - Free Tea!"}\ntag @s remove karak_new_vendor\n')
    for style in STYLES:
        value=seller_nbt(style,[0.,0.,0.]);value.pop('id');value.pop('Pos');value['Tags'].append('karak_new_vendor')
        fn('spawn_'+style,f'summon minecraft:villager ~ ~ ~ {snbt(value)}\n')
        marker=anchor_nbt(style,[0.,0.,0.]);marker.pop('id');marker.pop('Pos');marker['Tags'].append('karak_installing')
        fn('install_'+style,
           'execute if entity @e[type=minecraft:marker,tag=karak_anchor,distance=..0.25] run return 0\n'
           f'summon minecraft:marker ~ ~ ~ {snbt(marker)}\n'
           'execute as @e[type=minecraft:marker,tag=karak_installing,distance=..0.25,limit=1] at @s run function karak_house:stations/init\n'
           'execute as @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] run function karak_house:stations/upgrade_existing\n'
           'tag @e[tag=karak_installing,distance=..0.25] remove karak_installing\n')
    fn('upgrade_existing','function karak_house:stations/harden\ndata merge entity @s {Health:200.0f}\nfunction karak_house:stations/harden\n')
