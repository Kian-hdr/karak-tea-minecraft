effect clear @s minecraft:regeneration
execute if score @s karak_l_regn matches 1.. run function karak_house:powers/prepare/regeneration
