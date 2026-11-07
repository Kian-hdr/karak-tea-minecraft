scoreboard players set @s karak_legacy 0
execute store result score @s karak_legacy run data get entity @s active_effects[{id:"minecraft:fire_resistance"}].duration
execute if score @s karak_legacy matches 1.. run scoreboard players operation @s karak_t_reg = @s karak_legacy
execute if score @s karak_legacy matches 1.. run effect clear @s minecraft:slow_falling
execute if score @s karak_legacy matches 1.. run scoreboard players set @s karak_dirty 1
execute if score @s karak_legacy matches 1.. run tag @s add karak_stack_ready
