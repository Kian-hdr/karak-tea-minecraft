scoreboard players set @s karak_t_reg 0
scoreboard players set @s karak_t_iced 0
scoreboard players set @s karak_t_decaf 0
scoreboard players set @s karak_t_pro 0
scoreboard players set @s karak_t_milk 0
scoreboard players set @s karak_t_protein 0
execute if score @s karak_p_str matches 1.. run effect clear @s minecraft:strength
scoreboard players set @s karak_p_str 0
scoreboard players set @s karak_l_str 0
execute if score @s karak_p_spd matches 1.. run effect clear @s minecraft:speed
scoreboard players set @s karak_p_spd 0
scoreboard players set @s karak_l_spd 0
execute if score @s karak_p_jmp matches 1.. run effect clear @s minecraft:jump_boost
scoreboard players set @s karak_p_jmp 0
scoreboard players set @s karak_l_jmp 0
execute if score @s karak_p_res matches 1.. run effect clear @s minecraft:resistance
scoreboard players set @s karak_p_res 0
scoreboard players set @s karak_l_res 0
execute if score @s karak_p_regn matches 1.. run effect clear @s minecraft:regeneration
scoreboard players set @s karak_p_regn 0
scoreboard players set @s karak_l_regn 0
execute if score @s karak_p_fire matches 1.. run effect clear @s minecraft:fire_resistance
scoreboard players set @s karak_p_fire 0
scoreboard players set @s karak_l_fire 0
execute if score @s karak_p_water matches 1.. run effect clear @s minecraft:water_breathing
scoreboard players set @s karak_p_water 0
scoreboard players set @s karak_l_water 0
execute if score @s karak_p_night matches 1.. run effect clear @s minecraft:night_vision
scoreboard players set @s karak_p_night 0
scoreboard players set @s karak_l_night 0
function karak_house:powers/remove_fall
tag @s remove karak_drinker
tag @s add karak_stack_ready
scoreboard players set @s karak_dirty 0
scoreboard players set @s karak_refresh 0
scoreboard players set @s karak_died 0
