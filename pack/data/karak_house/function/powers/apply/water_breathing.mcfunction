effect clear @s minecraft:water_breathing
execute if score @s karak_l_water matches 1.. run function karak_house:powers/prepare/water_breathing
