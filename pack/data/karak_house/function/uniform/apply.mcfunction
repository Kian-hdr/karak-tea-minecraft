execute unless entity @s[type=minecraft:villager,tag=karak_seller] run return 0
execute if entity @s[tag=karak_uniform_chef_cap_1] run return 0
data merge entity @s {VillagerData:{profession:"minecraft:butcher"}}
execute unless data entity @s equipment.head run function karak_house:uniform/equip_cap
tag @s add karak_uniform_chef_cap_1
