attribute @s minecraft:fall_damage_multiplier modifier remove karak_house:tea_no_fall
attribute @s minecraft:fall_damage_multiplier modifier add karak_house:tea_no_fall -1 add_multiplied_total
tag @s add karak_no_fall
scoreboard players set @s karak_owned 1
