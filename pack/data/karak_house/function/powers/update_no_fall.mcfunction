scoreboard players set @s karak_fall 0
execute if score @s karak_t_reg matches 1.. run scoreboard players set @s karak_fall 1
execute if score @s karak_t_pro matches 1.. run scoreboard players set @s karak_fall 1
execute store success score @s karak_owned run attribute @s minecraft:fall_damage_multiplier modifier value get karak_house:tea_no_fall
execute if score @s karak_fall matches 1 unless score @s karak_owned matches 1 run function karak_house:powers/reapply
execute if score @s karak_fall matches 0 if score @s karak_owned matches 1 run function karak_house:powers/remove_fall
execute if score @s karak_fall matches 1 run tag @s add karak_no_fall
execute if score @s karak_fall matches 0 run tag @s remove karak_no_fall
