"""Village pool additions for Karak Houses.

On pinned Horizon 66f3981, guaranteed entries are tried first but still undergo
rotation, connector matching and collision checks. `count` is a strict upper
limit, not a promise that a house fits. Limits are shared by identical element
JSON within one structure start, not by mod namespace across different JSON.

Normal and abandoned villages use separate house pools. Both receive the same
serialized gate, so their placements share one limit within a structure start.
Their existing fallback pools receive that same gate too: at maximum layout
depth Horizon tries only the fallback. Incompatible street connectors still
reject the house by its building_entrance name.
Each vanilla village style reaches only its own house addition. Keep exactly one
Karak element key reachable from each start; validate_villages.py audits this
against actual prepared vanilla templates. Other mods require a fresh audit.
"""


def write_worldgen(write, themes):
    for style in themes:
        targets = [f'minecraft:village/{style}/houses',
                   f'minecraft:village/{style}/zombie/houses',
                   f'minecraft:village/{style}/terminators']
        # These two styles have a separate abandoned-village fallback. The
        # others reuse the normal terminators pool. Do not invent missing ids.
        if style in ('desert', 'savanna'):
            targets.append(f'minecraft:village/{style}/zombie/terminators')
        single = {'element_type': 'minecraft:single_pool_element',
                  'location': 'karak_house:village/karak_house_' + style,
                  'processors': {'processors': []}, 'projection': 'rigid'}
        gate = {'element_type': 'lithostitched:guaranteed', 'count': 1,
                'min_depth': 0, 'delegate': single}
        write(f'data/karak_house/worldgen/template_pool/additions/{style}.json',
              {'horizon:add_to': targets,
               'elements': [{'weight': 1, 'element': gate}]})
