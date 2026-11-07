effect clear @s minecraft:night_vision
execute if score @s karak_l_night matches 1.. run function karak_house:powers/prepare/night_vision
