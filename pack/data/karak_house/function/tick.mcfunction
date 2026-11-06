execute store result score #today karak_sys run time of minecraft:overworld query day repetition
execute as @e[type=minecraft:villager,tag=karak_seller] unless score @s karak_day matches 0.. run scoreboard players set @s karak_day -1
execute as @e[type=minecraft:villager,tag=karak_seller] if score @s karak_day < #today karak_sys run function karak_house:new_day
