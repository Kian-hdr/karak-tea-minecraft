"""Content-only Karak Tea gameplay definitions for Horizon 66f3981.

The repeating advancement is intentional: this engine's server tick function
context fails the camera predicate, whereas player advancement rewards resolve it.
"""

def write_gameplay(write):
    write('data/karak_house/function/load.mcfunction',
        'scoreboard objectives add karak_day dummy\nscoreboard objectives add karak_free dummy\nscoreboard objectives add karak_sys dummy\nscoreboard objectives add karak_talk minecraft.custom:minecraft.talked_to_villager\n'
        'function karak_house:powers/load\n'
        'function karak_house:stations/load\n'
        'function karak_house:doors/load\n')
    write('data/karak_house/function/tick.mcfunction',
        'function karak_house:powers/tick\n'
        'execute as @e[type=minecraft:villager,tag=karak_seller,tag=!karak_catalog_020_six] run function karak_house:catalog/upgrade_seller\n'
        'execute store result score #today karak_sys run time of minecraft:overworld query day repetition\n'
        'execute as @e[type=minecraft:villager,tag=karak_seller] unless score @s karak_day matches 0.. run scoreboard players set @s karak_day -1\n'
        'execute as @e[type=minecraft:villager,tag=karak_seller] if score @s karak_day < #today karak_sys run function karak_house:new_day\n'
        # Villager jump bases are not restored from NBT on this pinned engine.
        'execute as @e[type=minecraft:villager,tag=karak_seller] run function karak_house:stations/harden\n'
        'function karak_house:stations/tick\n'
        'function karak_house:doors/tick\n')
    write('data/karak_house/function/new_day.mcfunction',
        'scoreboard players operation @s karak_day = #today karak_sys\n'
        'data modify entity @s Offers.Recipes[].uses set value 0\n'
        'execute store result score @s karak_free run random value 1..10\n'
        'execute unless score @s karak_free matches 1 run scoreboard players set @s karak_free 0\n'
        'data merge entity @s {CustomName:"Karak Seller"}\n'
        'execute if score @s karak_free matches 1 run data merge entity @s {CustomName:"Karak Seller - Free Tea!"}\n')
    # Kept as a reusable broad predicate; selection below uses the narrower
    # temporary target tag so a closer seller cannot steal the clicked one's cup.
    for name, tag in [('looking_at_seller', 'karak_seller'), ('looking_at_target', 'karak_target')]:
        write(f'data/karak_house/predicate/{name}.json', {
            'type':'minecraft:entity_properties','entity':'this',
            'predicate':{'minecraft:type_specific/player':{'looking_at':{
                'minecraft:entity_type':'minecraft:villager','minecraft:nbt':f'{{Tags:["{tag}"]}}'}}}})
    # The NBT reference also activates this pinned engine's lazy entity-NBT views.
    write('data/karak_house/advancement/entity_context.json', {'criteria':{'context':{'trigger':'minecraft:impossible','conditions':{'player':[{'type':'minecraft:entity_properties','entity':'this','predicate':{'minecraft:nbt':'{Tags:["karak_seller"]}'}}]}}}})
    # This tautology always ticks, including when looking away, so old talk
    # events are cleared. The reference also opts this trigger into the engine's
    # lazy looking-at context; removing it breaks the reward-time predicate.
    write('data/karak_house/advancement/player_tick.json', {
        'criteria':{'tick':{'trigger':'minecraft:tick','conditions':{'player':{'type':'minecraft:any_of','terms':[{'type':'minecraft:reference','name':'karak_house:looking_at_seller'},{'type':'minecraft:inverted','term':{'type':'minecraft:reference','name':'karak_house:looking_at_seller'}}]}}}},
        'rewards':{'function':'karak_house:player_tick'}})
    write('data/karak_house/function/player_tick.mcfunction',
        'execute if score @s karak_talk matches 1.. if predicate karak_house:looking_at_seller run function karak_house:interact\n'
        'scoreboard players set @s karak_talk 0\n'
        'advancement revoke @s only karak_house:player_tick\n')
    write('data/karak_house/function/interact.mcfunction',
        'tag @e[tag=karak_target] remove karak_target\n'
        'tag @e[tag=karak_unchecked] remove karak_unchecked\n'
        'tag @e[type=minecraft:villager,tag=karak_seller,distance=..6] add karak_unchecked\n'
        'function karak_house:check_target\n'
        )
    write('data/karak_house/function/check_target.mcfunction',
        'tag @e[type=minecraft:villager,tag=karak_unchecked,sort=nearest,limit=1] add karak_target\n'
        'execute if predicate karak_house:looking_at_target run function karak_house:claim_target\n'
        'tag @e[tag=karak_target] remove karak_unchecked\n'
        'tag @e[tag=karak_target] remove karak_target\n'
        'execute if entity @e[tag=karak_unchecked] run function karak_house:check_target\n')
    write('data/karak_house/function/claim_target.mcfunction',
        'execute if score @e[type=minecraft:villager,tag=karak_target,limit=1] karak_free matches 1 run function karak_house:giveaway\n')
    write('data/karak_house/function/giveaway.mcfunction',
        'scoreboard players set @e[type=minecraft:villager,tag=karak_target,limit=1] karak_free 0\n'
        'function karak_house:stations/commit_claim\n'
        'data merge entity @e[type=minecraft:villager,tag=karak_target,limit=1] {CustomName:"Karak Seller"}\n'
        'give @s karak_house:karak_tea 1\n'
        'tellraw @s {"text":"This Karak Tea is on the house!","color":"gold"}\n')

    # Explicit saved-world repair: caller supplies the known booth position.
    # Does not touch offers, profession, stock, eligibility or the villager brain.
    write('data/karak_house/function/station_seller.mcfunction',
        'execute unless entity @s[type=minecraft:villager,tag=karak_seller] run return fail\n'
        'data merge entity @s {Motion:[0.0d,0.0d,0.0d]}\n'
        'tp @s ~ ~ ~\n'
        'attribute @s minecraft:movement_speed base set 0\n'
        'attribute @s minecraft:jump_strength base set 0\n')
