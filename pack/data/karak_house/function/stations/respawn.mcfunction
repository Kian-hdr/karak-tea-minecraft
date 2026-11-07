scoreboard players operation #saved_day karak_sys = @s karak_day
scoreboard players operation #saved_free karak_sys = @s karak_free
execute if entity @s[tag=karak_style_plains] run function karak_house:stations/spawn_plains
execute if entity @s[tag=karak_style_desert] run function karak_house:stations/spawn_desert
execute if entity @s[tag=karak_style_savanna] run function karak_house:stations/spawn_savanna
execute if entity @s[tag=karak_style_taiga] run function karak_house:stations/spawn_taiga
execute if entity @s[tag=karak_style_snowy] run function karak_house:stations/spawn_snowy
execute as @e[tag=karak_new_vendor,distance=..1,limit=1] run function karak_house:stations/restore
scoreboard players set @s karak_wait 0
