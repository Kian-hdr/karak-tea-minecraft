tp @s ~ ~ ~ ~ ~
scoreboard players operation @s karak_sid = #station karak_sys
scoreboard players operation @s karak_day = #saved_day karak_sys
scoreboard players operation @s karak_free = #saved_free karak_sys
function karak_house:stations/harden
tag @s remove karak_new_vendor
