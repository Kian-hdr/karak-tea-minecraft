tag @e[type=minecraft:villager,tag=karak_unchecked,sort=nearest,limit=1] add karak_target
execute if predicate karak_house:looking_at_target run function karak_house:claim_target
tag @e[tag=karak_target] remove karak_unchecked
tag @e[tag=karak_target] remove karak_target
execute if entity @e[tag=karak_unchecked] run function karak_house:check_target
