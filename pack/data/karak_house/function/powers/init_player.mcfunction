function karak_house:powers/active_flags
execute if score @s karak_any matches 1 run tag @s add karak_stack_ready
execute if score @s karak_any matches 0 if predicate karak_house:powers/legacy_regular run function karak_house:powers/migrate_regular
execute if score @s karak_any matches 0 unless predicate karak_house:powers/legacy_regular run tag @s add karak_stack_ready
