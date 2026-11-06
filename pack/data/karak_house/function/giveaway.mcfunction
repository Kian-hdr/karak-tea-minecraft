scoreboard players set @s karak_free 0
data merge entity @s {CustomName:"Karak Seller"}
give @a[tag=karak_customer,limit=1] karak_house:karak_tea 1
tellraw @a[tag=karak_customer,limit=1] {"text":"This Karak Tea is on the house!","color":"gold"}
