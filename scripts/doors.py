"""Pair only the two authored Karak entry leaves through the existing anchor.

No template dimensions, door/plate geometry or block appearance changes. Local
coordinates refer to cell centers, so rotated anchors cannot cross a boundary.
"""


def write_doors(write, themes):
    def fn(name, value):
        write(f'data/karak_house/function/doors/{name}.mcfunction', value)

    fn('load', 'scoreboard objectives add karak_door dummy\n')
    tick = ''
    for style, theme in themes.items():
        wood = theme['wood']
        forward = theme['depth'] - 8
        for yaw, facing in ((180,'south'),(270,'west'),(0,'north'),(90,'east')):
            # Generic marker entities do not retain useful yaw on this pinned
            # engine. Require the complete authored entry fingerprint instead.
            line = (f'execute as @e[type=minecraft:marker,tag=karak_anchor,tag=karak_style_{style}] '
                    f'at @s rotated {yaw} 0 ')
            for left in (0,-1):
                line += f'if block ^{left} ^0 ^{forward} minecraft:{wood}_door[facing={facing},half=lower] '
                for distance in (forward+1,forward-1):
                    line += f'if block ^{left} ^0 ^{distance} minecraft:{wood}_pressure_plate '
            tick += line + f'run function karak_house:doors/watch_{style}\n'
        watch = ('execute unless score @s karak_door matches 0.. run scoreboard players set @s karak_door 0\n'
                 'scoreboard players set #paired_open karak_sys 0\n')
        for left in (0, -1):
            for distance in (forward + 1, forward - 1):
                watch += (f'execute positioned ^{left} ^0 ^{distance} '
                          f'if block ~ ~ ~ minecraft:{wood}_pressure_plate[powered=true] '
                          'run scoreboard players set #paired_open karak_sys 1\n')
        watch += (f'execute if score #paired_open karak_sys matches 1 run function karak_house:doors/open_{style}\n'
                  f'execute if score #paired_open karak_sys matches 0 if score @s karak_door matches 1 run function karak_house:doors/close_{style}\n'
                  'scoreboard players operation @s karak_door = #paired_open karak_sys\n')
        fn('watch_' + style, watch)
        for target in ('open', 'close'):
            value = 'true' if target == 'open' else 'false'
            prior = 'false' if target == 'open' else 'true'
            commands = ''
            for left in (0, -1):
                for dy, half in ((0, 'lower'), (1, 'upper')):
                    for facing in ('north', 'east', 'south', 'west'):
                        for hinge in ('left', 'right'):
                            for powered in ('false', 'true'):
                                other = f'facing={facing},half={half},hinge={hinge},powered={powered}'
                                commands += (f'execute positioned ^{left} ^{dy} ^{forward} '
                                             f'if block ~ ~ ~ minecraft:{wood}_door[{other},open={prior}] '
                                             f'run setblock ~ ~ ~ minecraft:{wood}_door[{other},open={value}]\n')
            fn(target + '_' + style, commands)
    fn('tick', tick)
