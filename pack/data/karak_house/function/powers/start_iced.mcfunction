execute unless entity @s[tag=karak_stack_ready] run function karak_house:powers/init_player
scoreboard players set @s karak_t_iced 6000
scoreboard players set @s karak_refresh 2
scoreboard players set @s karak_dirty 1
scoreboard players set @s karak_died 0
effect clear @s minecraft:slow_falling
function karak_house:powers/recompute
advancement revoke @s only karak_house:powers/drank_iced
