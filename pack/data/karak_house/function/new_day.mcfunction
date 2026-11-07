scoreboard players operation @s karak_day = #today karak_sys
data modify entity @s Offers.Recipes[].uses set value 0
execute store result score @s karak_free run random value 1..10
execute unless score @s karak_free matches 1 run scoreboard players set @s karak_free 0
data merge entity @s {CustomName:"Karak Seller"}
execute if score @s karak_free matches 1 run data merge entity @s {CustomName:"Karak Seller - Free Tea!"}
