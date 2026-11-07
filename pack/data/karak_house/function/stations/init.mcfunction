scoreboard players add #next_station karak_sys 1
scoreboard players operation @s karak_sid = #next_station karak_sys
scoreboard players set @s karak_wait 0
scoreboard players set @s karak_day -1
scoreboard players set @s karak_free 0
scoreboard players operation #station karak_sys = @s karak_sid
execute as @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] unless score @s karak_sid matches 1.. run scoreboard players operation @s karak_sid = #station karak_sys
scoreboard players operation @s karak_day = @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] karak_day
scoreboard players operation @s karak_free = @e[type=minecraft:villager,tag=karak_seller,distance=..1,sort=nearest,limit=1] karak_free
