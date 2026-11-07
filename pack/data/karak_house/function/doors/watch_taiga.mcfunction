execute unless score @s karak_door matches 0.. run scoreboard players set @s karak_door 0
scoreboard players set #paired_open karak_sys 0
execute positioned ^0 ^0 ^6 if block ~ ~ ~ minecraft:spruce_pressure_plate[powered=true] run scoreboard players set #paired_open karak_sys 1
execute positioned ^0 ^0 ^4 if block ~ ~ ~ minecraft:spruce_pressure_plate[powered=true] run scoreboard players set #paired_open karak_sys 1
execute positioned ^-1 ^0 ^6 if block ~ ~ ~ minecraft:spruce_pressure_plate[powered=true] run scoreboard players set #paired_open karak_sys 1
execute positioned ^-1 ^0 ^4 if block ~ ~ ~ minecraft:spruce_pressure_plate[powered=true] run scoreboard players set #paired_open karak_sys 1
execute if score #paired_open karak_sys matches 1 run function karak_house:doors/open_taiga
execute if score #paired_open karak_sys matches 0 if score @s karak_door matches 1 run function karak_house:doors/close_taiga
scoreboard players operation @s karak_door = #paired_open karak_sys
