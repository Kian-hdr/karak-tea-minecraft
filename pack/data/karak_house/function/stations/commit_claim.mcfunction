execute unless score @e[tag=karak_target,limit=1] karak_sid matches 1.. run return 0
scoreboard players operation #claimed_station karak_sys = @e[tag=karak_target,limit=1] karak_sid
execute as @e[type=minecraft:marker,tag=karak_anchor] if score @s karak_sid = #claimed_station karak_sys run scoreboard players set @s karak_free 0
