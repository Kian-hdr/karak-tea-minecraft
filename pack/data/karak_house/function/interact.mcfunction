tag @s add karak_customer
execute at @s as @e[type=minecraft:villager,tag=karak_seller,distance=..6,sort=nearest,limit=1] if score @s karak_free matches 1 run function karak_house:giveaway
tag @s remove karak_customer
