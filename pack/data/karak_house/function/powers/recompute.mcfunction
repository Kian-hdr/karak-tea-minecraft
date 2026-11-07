scoreboard players set @s karak_l_str 0
scoreboard players set @s karak_m_str 0
execute if score @s karak_t_reg matches 1.. run scoreboard players add @s karak_l_str 4
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_str > @s karak_t_reg
execute if score @s karak_t_pro matches 1.. run scoreboard players add @s karak_l_str 6
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_str > @s karak_t_pro
execute if score @s karak_t_protein matches 1.. run scoreboard players add @s karak_l_str 7
execute if score @s karak_t_protein matches 1.. run scoreboard players operation @s karak_m_str > @s karak_t_protein
execute unless score @s karak_p_str matches 0.. run scoreboard players set @s karak_p_str 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_str = @s karak_p_str run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 6 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_str matches 1.. unless predicate karak_house:powers/present/strength run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/strength
scoreboard players operation @s karak_p_str = @s karak_l_str
scoreboard players set @s karak_l_spd 0
scoreboard players set @s karak_m_spd 0
execute if score @s karak_t_reg matches 1.. run scoreboard players add @s karak_l_spd 3
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_spd > @s karak_t_reg
execute if score @s karak_t_pro matches 1.. run scoreboard players add @s karak_l_spd 4
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_spd > @s karak_t_pro
execute unless score @s karak_p_spd matches 0.. run scoreboard players set @s karak_p_spd 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_spd = @s karak_p_spd run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_spd matches 1.. unless predicate karak_house:powers/present/speed run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/speed
scoreboard players operation @s karak_p_spd = @s karak_l_spd
scoreboard players set @s karak_l_jmp 0
scoreboard players set @s karak_m_jmp 0
execute if score @s karak_t_reg matches 1.. run scoreboard players add @s karak_l_jmp 3
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_jmp > @s karak_t_reg
execute if score @s karak_t_pro matches 1.. run scoreboard players add @s karak_l_jmp 4
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_jmp > @s karak_t_pro
execute unless score @s karak_p_jmp matches 0.. run scoreboard players set @s karak_p_jmp 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_jmp = @s karak_p_jmp run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_jmp matches 1.. unless predicate karak_house:powers/present/jump_boost run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/jump_boost
scoreboard players operation @s karak_p_jmp = @s karak_l_jmp
scoreboard players set @s karak_l_res 0
scoreboard players set @s karak_m_res 0
execute if score @s karak_t_reg matches 1.. run scoreboard players add @s karak_l_res 2
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_res > @s karak_t_reg
execute if score @s karak_t_pro matches 1.. run scoreboard players add @s karak_l_res 3
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_res > @s karak_t_pro
execute unless score @s karak_p_res matches 0.. run scoreboard players set @s karak_p_res 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_res = @s karak_p_res run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_res matches 1.. unless predicate karak_house:powers/present/resistance run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/resistance
scoreboard players operation @s karak_p_res = @s karak_l_res
scoreboard players set @s karak_l_regn 0
scoreboard players set @s karak_m_regn 0
execute if score @s karak_t_reg matches 1.. run scoreboard players add @s karak_l_regn 1
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_regn > @s karak_t_reg
execute if score @s karak_t_decaf matches 1.. run scoreboard players add @s karak_l_regn 1
execute if score @s karak_t_decaf matches 1.. run scoreboard players operation @s karak_m_regn > @s karak_t_decaf
execute if score @s karak_t_pro matches 1.. run scoreboard players add @s karak_l_regn 2
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_regn > @s karak_t_pro
execute unless score @s karak_p_regn matches 0.. run scoreboard players set @s karak_p_regn 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_regn = @s karak_p_regn run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 3 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_regn matches 1.. unless predicate karak_house:powers/present/regeneration run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/regeneration
scoreboard players operation @s karak_p_regn = @s karak_l_regn
scoreboard players set @s karak_l_fire 0
scoreboard players set @s karak_m_fire 0
execute if score @s karak_t_reg matches 1.. run scoreboard players set @s karak_l_fire 1
execute if score @s karak_t_reg matches 1.. run scoreboard players operation @s karak_m_fire > @s karak_t_reg
execute if score @s karak_t_iced matches 1.. run scoreboard players set @s karak_l_fire 1
execute if score @s karak_t_iced matches 1.. run scoreboard players operation @s karak_m_fire > @s karak_t_iced
execute if score @s karak_t_pro matches 1.. run scoreboard players set @s karak_l_fire 1
execute if score @s karak_t_pro matches 1.. run scoreboard players operation @s karak_m_fire > @s karak_t_pro
execute unless score @s karak_p_fire matches 0.. run scoreboard players set @s karak_p_fire 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_fire = @s karak_p_fire run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 1 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 2 run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 4 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_fire matches 1.. unless predicate karak_house:powers/present/fire_resistance run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/fire_resistance
scoreboard players operation @s karak_p_fire = @s karak_l_fire
scoreboard players set @s karak_l_water 0
scoreboard players set @s karak_m_water 0
execute if score @s karak_t_iced matches 1.. run scoreboard players set @s karak_l_water 1
execute if score @s karak_t_iced matches 1.. run scoreboard players operation @s karak_m_water > @s karak_t_iced
execute unless score @s karak_p_water matches 0.. run scoreboard players set @s karak_p_water 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_water = @s karak_p_water run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 2 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_water matches 1.. unless predicate karak_house:powers/present/water_breathing run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/water_breathing
scoreboard players operation @s karak_p_water = @s karak_l_water
scoreboard players set @s karak_l_night 0
scoreboard players set @s karak_m_night 0
execute if score @s karak_t_decaf matches 1.. run scoreboard players set @s karak_l_night 1
execute if score @s karak_t_decaf matches 1.. run scoreboard players operation @s karak_m_night > @s karak_t_decaf
execute unless score @s karak_p_night matches 0.. run scoreboard players set @s karak_p_night 0
scoreboard players set @s karak_apply 0
execute unless score @s karak_l_night = @s karak_p_night run scoreboard players set @s karak_apply 1
execute if score @s karak_refresh matches 3 run scoreboard players set @s karak_apply 1
execute if score @s karak_l_night matches 1.. unless predicate karak_house:powers/present/night_vision run scoreboard players set @s karak_apply 1
execute if score @s karak_apply matches 1 run function karak_house:powers/apply/night_vision
scoreboard players operation @s karak_p_night = @s karak_l_night
function karak_house:powers/active_flags
execute if score @s karak_any matches 1 run tag @s add karak_drinker
execute if score @s karak_any matches 0 run tag @s remove karak_drinker
scoreboard players set @s karak_dirty 0
scoreboard players set @s karak_refresh 0
function karak_house:powers/update_no_fall
