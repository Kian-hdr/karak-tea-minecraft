execute if entity @e[type=minecraft:marker,tag=karak_anchor,distance=..0.25] run return 0
summon minecraft:marker ~ ~ ~ {"Tags":["karak_anchor","karak_style_plains","karak_installing"],"Rotation":[180.0,0.0]}
execute as @e[type=minecraft:marker,tag=karak_installing,distance=..0.25,limit=1] at @s run function karak_house:stations/init
execute as @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] run function karak_house:stations/upgrade_existing
tag @e[tag=karak_installing,distance=..0.25] remove karak_installing
