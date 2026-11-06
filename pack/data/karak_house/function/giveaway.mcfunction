scoreboard players set @e[type=minecraft:villager,tag=karak_target,limit=1] karak_free 0
data merge entity @e[type=minecraft:villager,tag=karak_target,limit=1] {CustomName:"Karak Seller"}
give @s karak_house:karak_tea 1
tellraw @s {"text":"This Karak Tea is on the house!","color":"gold"}
