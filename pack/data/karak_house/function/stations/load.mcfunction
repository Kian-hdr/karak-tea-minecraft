scoreboard objectives add karak_sid dummy
scoreboard objectives add karak_wait dummy
execute unless score #next_station karak_sys matches 0.. run scoreboard players set #next_station karak_sys 0
