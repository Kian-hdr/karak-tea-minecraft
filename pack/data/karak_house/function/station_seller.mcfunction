execute unless entity @s[type=minecraft:villager,tag=karak_seller] run return fail
data merge entity @s {Motion:[0.0d,0.0d,0.0d]}
tp @s ~ ~ ~
attribute @s minecraft:movement_speed base set 0
attribute @s minecraft:jump_strength base set 0
