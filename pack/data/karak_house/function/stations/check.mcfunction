execute unless score @s karak_sid matches 1.. run function karak_house:stations/init
scoreboard players operation #station karak_sys = @s karak_sid
tag @e[tag=karak_station_vendor] remove karak_station_vendor
execute as @e[type=minecraft:villager,tag=karak_seller,nbt=!{Health:0.0f}] if score @s karak_sid = #station karak_sys run tag @s add karak_station_vendor
execute if entity @e[tag=karak_station_vendor] run function karak_house:stations/snapshot
execute unless entity @e[tag=karak_station_vendor] run scoreboard players add @s karak_wait 1
execute if score @s karak_wait matches 100.. run function karak_house:stations/respawn
tag @e[tag=karak_station_vendor] remove karak_station_vendor
