execute if score @s karak_talk matches 1.. if predicate karak_house:looking_at_seller run function karak_house:interact
scoreboard players set @s karak_talk 0
advancement revoke @s only karak_house:player_tick
