scoreboard players set @s karak_wait 0
scoreboard players operation @s karak_day = @e[tag=karak_station_vendor,limit=1] karak_day
scoreboard players operation @s karak_free = @e[tag=karak_station_vendor,limit=1] karak_free
