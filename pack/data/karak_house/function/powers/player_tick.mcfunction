execute unless entity @s[tag=karak_stack_ready] run function karak_house:powers/init_player
execute if score @s karak_died matches 1.. run function karak_house:powers/clear
execute if score @s karak_l_str matches 1.. unless predicate karak_house:powers/present/strength run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_spd matches 1.. unless predicate karak_house:powers/present/speed run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_jmp matches 1.. unless predicate karak_house:powers/present/jump_boost run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_res matches 1.. unless predicate karak_house:powers/present/resistance run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_regn matches 1.. unless predicate karak_house:powers/present/regeneration run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_fire matches 1.. unless predicate karak_house:powers/present/fire_resistance run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_water matches 1.. unless predicate karak_house:powers/present/water_breathing run scoreboard players set @s karak_dirty 1
execute if score @s karak_l_night matches 1.. unless predicate karak_house:powers/present/night_vision run scoreboard players set @s karak_dirty 1
execute if score @s karak_dirty matches 1.. run function karak_house:powers/recompute
function karak_house:powers/update_no_fall
execute if score @s karak_t_milk matches 1.. run function karak_house:powers/protect_tick
advancement revoke @s only karak_house:powers/player_tick
