function karak_house:powers/tick
execute as @e[type=minecraft:villager,tag=karak_seller,tag=!karak_catalog_020_six] run function karak_house:catalog/upgrade_seller
execute store result score #today karak_sys run time of minecraft:overworld query day repetition
execute as @e[type=minecraft:villager,tag=karak_seller] unless score @s karak_day matches 0.. run scoreboard players set @s karak_day -1
execute as @e[type=minecraft:villager,tag=karak_seller] if score @s karak_day < #today karak_sys run function karak_house:new_day
execute as @e[type=minecraft:villager,tag=karak_seller] run function karak_house:stations/harden
function karak_house:stations/tick
function karak_house:doors/tick
function karak_house:uniform/tick
