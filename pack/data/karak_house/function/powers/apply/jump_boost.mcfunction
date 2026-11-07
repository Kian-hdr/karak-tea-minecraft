effect clear @s minecraft:jump_boost
execute if score @s karak_l_jmp matches 1.. run function karak_house:powers/prepare/jump_boost
