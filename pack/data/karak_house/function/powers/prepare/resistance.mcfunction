data modify storage karak_house:powers args set value {seconds:1,amplifier:0}
scoreboard players operation @s karak_secs = @s karak_m_res
scoreboard players add @s karak_secs 19
scoreboard players operation @s karak_secs /= #twenty karak_const
scoreboard players operation @s karak_amp = @s karak_l_res
scoreboard players remove @s karak_amp 1
execute store result storage karak_house:powers args.seconds int 1 run scoreboard players get @s karak_secs
execute store result storage karak_house:powers args.amplifier int 1 run scoreboard players get @s karak_amp
function karak_house:powers/macro/resistance with storage karak_house:powers args
