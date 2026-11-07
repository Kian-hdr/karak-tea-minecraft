"""Stock-client chef cap plus vanilla butcher apron, scoped to Karak Sellers."""

MIGRATION_TAG = 'karak_uniform_chef_cap_1'


def write_chef_uniform(write):
    write('data/karak_house/horizon/item/chef_hat.json', {
        'template': 'minecraft:paper', 'max_stack_size': 1,
        'components': {'minecraft:item_name': 'Chef Cap',
                       'minecraft:item_model': 'karak_house:chef_hat'},
    })
    write('assets/karak_house/items/chef_hat.json', {
        'model': {'type': 'minecraft:model', 'model': 'karak_house:item/chef_hat'},
    })
    elements = []
    for name, start, end in (
        ('cap_band', [0.5, 3.0, 0.5], [15.5, 10, 15.5]),
        ('cap_crown', [0, 10, 0], [16, 14, 16]),
    ):
        elements.append({'name': name, 'from': start, 'to': end,
                         'faces': {face: {'texture': '#cream'} for face in
                                   ('north', 'south', 'east', 'west', 'up', 'down')}})
    write('assets/karak_house/models/item/chef_hat.json', {
        'parent': 'minecraft:block/block',
        'textures': {'cream': 'minecraft:block/quartz_block_bottom',
                     'particle': 'minecraft:block/quartz_block_bottom'},
        'elements': elements,
        'display': {'head': {'rotation': [0, 0, 0], 'translation': [0, 8, 0],
                             'scale': [1, 1, 1]}},
    })
    # Tick gate handles old saves, fresh structures and respawned sellers once.
    # Player equipment added/removed after migration remains the player's choice.
    write('data/karak_house/function/uniform/tick.mcfunction',
          f'execute as @e[type=minecraft:villager,tag=karak_seller,tag=!{MIGRATION_TAG}] run function karak_house:uniform/apply\n')
    write('data/karak_house/function/uniform/apply.mcfunction',
          'execute unless entity @s[type=minecraft:villager,tag=karak_seller] run return 0\n'
          f'execute if entity @s[tag={MIGRATION_TAG}] run return 0\n'
          'data merge entity @s {VillagerData:{profession:"minecraft:butcher"}}\n'
          'execute unless data entity @s equipment.head run function karak_house:uniform/equip_cap\n'
          f'tag @s add {MIGRATION_TAG}\n')
    # SNBT must explicitly use Float: the pinned engine ignores Double chances.
    write('data/karak_house/function/uniform/equip_cap.mcfunction',
          'data merge entity @s {equipment:{head:{id:"karak_house:chef_hat",count:1}},drop_chances:{head:0.0f}}\n')
