"""Independent Karak timers and additive vanilla-effect levels on Horizon 66f3981.

Server functions own time. Hidden player advancement rewards own effect and
attribute views. Recompute only changed/refreshed contribution types; dynamic
function arguments carry the remaining duration and uncapped amplifier.
"""

DURATION = 6000
MODIFIER = 'karak_house:tea_no_fall'
ATTRIBUTE = 'minecraft:fall_damage_multiplier'
ACTIVE = 'karak_no_fall'
DRINKER = 'karak_drinker'
READY = 'karak_stack_ready'
EFFECTS = [('strength', 3), ('speed', 2), ('jump_boost', 2),
           ('resistance', 1), ('regeneration', 0), ('fire_resistance', 0)]
VARIETIES = {
    'regular': {'number': 1, 'item': 'karak_house:karak_tea', 'name': 'Karak Tea',
                'duration': 6000, 'timer': 'karak_t_reg', 'no_fall': True, 'effects': EFFECTS,
                'start': 'start', 'advancement': 'drank_tea',
                'lore': ['5 minutes: Strength IV, Speed III, Jump Boost III.',
                         'Resistance II, Regeneration I, Fire Resistance; no fall damage.']},
    'iced': {'number': 2, 'item': 'karak_house:iced_karak', 'name': 'Iced Karak',
             'duration': 6000, 'timer': 'karak_t_iced', 'no_fall': False,
             'effects': [('fire_resistance', 0), ('water_breathing', 0)],
             'start': 'start_iced', 'advancement': 'drank_iced',
             'lore': ['5 minutes: Fire Resistance and Water Breathing.']},
    'decaf': {'number': 3, 'item': 'karak_house:decaf_karak', 'name': 'Decaf Karak',
              'duration': 6000, 'timer': 'karak_t_decaf', 'no_fall': False,
              'effects': [('night_vision', 0), ('regeneration', 0)],
              'start': 'start_decaf', 'advancement': 'drank_decaf',
              'lore': ['5 minutes: Night Vision and gentle Regeneration I.']},
    'pro_max': {'number': 4, 'item': 'karak_house:karak_pro_max', 'name': 'Karak Pro Max',
                'duration': 36000, 'timer': 'karak_t_pro', 'no_fall': True,
                'effects': [('strength', 5), ('speed', 3), ('jump_boost', 3),
                            ('resistance', 2), ('regeneration', 1), ('fire_resistance', 0)],
                'start': 'start_pro_max', 'advancement': 'drank_pro_max',
                'lore': ['30 minutes: Strength VI, Speed IV, Jump Boost IV.',
                         'Resistance III, Regeneration II, Fire Resistance; no fall damage.']},
    'milkshake': {'number': 5, 'item': 'karak_house:karak_milkshake', 'name': 'Karak Milkshake',
                  'duration': 6000, 'timer': 'karak_t_milk', 'no_fall': False, 'effects': [],
                  'start': 'start_milkshake', 'advancement': 'drank_milkshake',
                  'lore': ['Clears harmful effects; preserves other Karak bonuses.',
                           '5 minutes: protection from Poison, Nausea and Hunger.']},
    'protein_shake': {'number': 6, 'item': 'karak_house:karak_protein_shake', 'name': 'Karak Protein Shake',
                      'duration': 6000, 'timer': 'karak_t_protein', 'no_fall': False,
                      'effects': [('strength', 6)], 'start': 'start_protein_shake',
                      'advancement': 'drank_protein_shake',
                      'lore': ['5 minutes: Strength VII only.']},
}
BINARY = {'fire_resistance', 'water_breathing', 'night_vision'}
ALIASES = {'strength': 'str', 'speed': 'spd', 'jump_boost': 'jmp', 'resistance': 'res',
           'regeneration': 'regn', 'fire_resistance': 'fire', 'water_breathing': 'water', 'night_vision': 'night'}
# Pinned MobEffects Category::Harmful, including the four 1.21 effects.
HARMFUL = ['slowness', 'mining_fatigue', 'instant_damage', 'nausea', 'blindness',
           'hunger', 'weakness', 'poison', 'wither', 'levitation', 'unluck',
           'darkness', 'wind_charged', 'weaving', 'oozing', 'infested']
SHIELD_EFFECTS = ['poison', 'nausea', 'hunger']


def reconcile_owned_generated(pack_root, emitted_paths):
    """Prune stale generated hooks only within this module's owned directories."""
    from pathlib import Path
    root = Path(pack_root)
    expected = set(emitted_paths)
    removed = []
    for relative in ['data/karak_house/function/powers', 'data/karak_house/predicate/powers',
                     'data/karak_house/advancement/powers']:
        directory = root / relative
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path.relative_to(root).as_posix() not in expected:
                removed.append(path.relative_to(root).as_posix())
                path.unlink()
    return removed


def combined_levels(active):
    result = {}
    for key in active:
        for effect, amplifier in VARIETIES[key]['effects']:
            result[effect] = 1 if effect in BINARY else result.get(effect, 0) + amplifier + 1
    return result


def write_powers(write):
    prefix = 'data/karak_house/'
    written = set()

    def emit(path, value):
        written.add(path)
        write(path, value)

    def function(name, lines):
        emit(prefix + 'function/powers/' + name + '.mcfunction', '\n'.join(lines) + '\n')

    def consume_hook(name, item, reward):
        emit(prefix + 'advancement/powers/' + name + '.json', {
            'criteria': {'consume': {'trigger': 'minecraft:consume_item',
                                      'conditions': {'item': {'items': [item]}}}},
            'rewards': {'function': 'karak_house:powers/' + reward}})

    objectives = ['karak_dirty', 'karak_refresh', 'karak_apply', 'karak_amp', 'karak_secs',
                  'karak_owned', 'karak_any', 'karak_fall', 'karak_const', 'karak_legacy']
    objectives += [v['timer'] for v in VARIETIES.values()]
    objectives += ['karak_' + kind + '_' + alias for alias in ALIASES.values() for kind in ['l', 'm', 'p']]
    function('load', [f'scoreboard objectives add {name} dummy' for name in objectives] + [
        'scoreboard objectives add karak_died deathCount',
        'scoreboard players set #twenty karak_const 20',
        'execute as @a run scoreboard players set @s karak_dirty 1'])
    tick = []
    for data in VARIETIES.values():
        timer = data['timer']
        tick += [f'execute as @a[scores={{{timer}=1}}] run scoreboard players set @s karak_dirty 1',
                 f'scoreboard players remove @a[scores={{{timer}=1..}}] {timer} 1']
    function('tick', tick)
    function('active_flags', ['scoreboard players set @s karak_any 0'] + [
        f'execute if score @s {v["timer"]} matches 1.. run scoreboard players set @s karak_any 1'
        for v in VARIETIES.values()])
    function('reapply', [f'attribute @s {ATTRIBUTE} modifier remove {MODIFIER}',
                         f'attribute @s {ATTRIBUTE} modifier add {MODIFIER} -1 add_multiplied_total',
                         f'tag @s add {ACTIVE}', 'scoreboard players set @s karak_owned 1'])
    function('remove_fall', [f'attribute @s {ATTRIBUTE} modifier remove {MODIFIER}',
                             f'tag @s remove {ACTIVE}', 'scoreboard players set @s karak_owned 0'])
    function('update_no_fall', ['scoreboard players set @s karak_fall 0'] + [
        f'execute if score @s {v["timer"]} matches 1.. run scoreboard players set @s karak_fall 1'
        for v in VARIETIES.values() if v['no_fall']] + [
        f'execute store success score @s karak_owned run attribute @s {ATTRIBUTE} modifier value get {MODIFIER}',
        'execute if score @s karak_fall matches 1 unless score @s karak_owned matches 1 run function karak_house:powers/reapply',
        'execute if score @s karak_fall matches 0 if score @s karak_owned matches 1 run function karak_house:powers/remove_fall',
        f'execute if score @s karak_fall matches 1 run tag @s add {ACTIVE}',
        f'execute if score @s karak_fall matches 0 run tag @s remove {ACTIVE}'])

    # Import exactly the canonical old regular bundle once. Do not silently
    # reset it to five minutes: take its actual remaining native effect ticks.
    emit(prefix + 'predicate/powers/legacy_regular.json', {
        'type': 'minecraft:entity_properties', 'entity': 'this',
        'predicate': {'minecraft:effects': {'minecraft:' + effect:
            {'amplifier': {'min': amplifier, 'max': amplifier}} for effect, amplifier in EFFECTS}}})
    function('migrate_regular', ['scoreboard players set @s karak_legacy 0',
        'execute store result score @s karak_legacy run data get entity @s active_effects[{id:"minecraft:fire_resistance"}].duration',
        'execute if score @s karak_legacy matches 1.. run scoreboard players operation @s karak_t_reg = @s karak_legacy',
        'execute if score @s karak_legacy matches 1.. run effect clear @s minecraft:slow_falling',
        'execute if score @s karak_legacy matches 1.. run scoreboard players set @s karak_dirty 1',
        f'execute if score @s karak_legacy matches 1.. run tag @s add {READY}'])
    function('init_player', ['function karak_house:powers/active_flags',
        f'execute if score @s karak_any matches 1 run tag @s add {READY}',
        'execute if score @s karak_any matches 0 if predicate karak_house:powers/legacy_regular run function karak_house:powers/migrate_regular',
        f'execute if score @s karak_any matches 0 unless predicate karak_house:powers/legacy_regular run tag @s add {READY}'])
    function('clear_harmful', ['effect clear @s minecraft:' + effect for effect in HARMFUL])
    function('protect_tick', ['effect clear @s minecraft:' + effect for effect in SHIELD_EFFECTS])

    recompute = []
    for effect, alias in ALIASES.items():
        level, maximum, previous = ['karak_' + k + '_' + alias for k in ['l', 'm', 'p']]
        contributors = [(v, dict(v['effects'])[effect] + 1) for v in VARIETIES.values() if effect in dict(v['effects'])]
        recompute += [f'scoreboard players set @s {level} 0', f'scoreboard players set @s {maximum} 0']
        for data, amount in contributors:
            action = f'scoreboard players set @s {level} 1' if effect in BINARY else f'scoreboard players add @s {level} {amount}'
            recompute += [f'execute if score @s {data["timer"]} matches 1.. run {action}',
                          f'execute if score @s {data["timer"]} matches 1.. run scoreboard players operation @s {maximum} > @s {data["timer"]}']
        recompute += [f'execute unless score @s {previous} matches 0.. run scoreboard players set @s {previous} 0',
                      'scoreboard players set @s karak_apply 0',
                      f'execute unless score @s {level} = @s {previous} run scoreboard players set @s karak_apply 1']
        recompute += [f'execute if score @s karak_refresh matches {v["number"]} run scoreboard players set @s karak_apply 1' for v, _ in contributors]
        recompute += [f'execute if score @s {level} matches 1.. unless predicate karak_house:powers/present/{effect} run scoreboard players set @s karak_apply 1',
                      f'execute if score @s karak_apply matches 1 run function karak_house:powers/apply/{effect}',
                      f'scoreboard players operation @s {previous} = @s {level}']
        emit(prefix + 'predicate/powers/present/' + effect + '.json', {
            'type': 'minecraft:entity_properties', 'entity': 'this',
            'predicate': {'minecraft:effects': {'minecraft:' + effect: {}}}})
        function('apply/' + effect, [f'effect clear @s minecraft:{effect}',
            f'execute if score @s {level} matches 1.. run function karak_house:powers/prepare/{effect}'])
        function('prepare/' + effect, [
            'data modify storage karak_house:powers args set value {seconds:1,amplifier:0}',
            f'scoreboard players operation @s karak_secs = @s {maximum}',
            'scoreboard players add @s karak_secs 19',
            'scoreboard players operation @s karak_secs /= #twenty karak_const',
            f'scoreboard players operation @s karak_amp = @s {level}',
            'scoreboard players remove @s karak_amp 1',
            'execute store result storage karak_house:powers args.seconds int 1 run scoreboard players get @s karak_secs',
            'execute store result storage karak_house:powers args.amplifier int 1 run scoreboard players get @s karak_amp',
            f'function karak_house:powers/macro/{effect} with storage karak_house:powers args'])
        function('macro/' + effect, [f'$effect give @s minecraft:{effect} $(seconds) $(amplifier) false'])
    recompute += ['function karak_house:powers/active_flags',
                  f'execute if score @s karak_any matches 1 run tag @s add {DRINKER}',
                  f'execute if score @s karak_any matches 0 run tag @s remove {DRINKER}',
                  'scoreboard players set @s karak_dirty 0', 'scoreboard players set @s karak_refresh 0',
                  'function karak_house:powers/update_no_fall']
    function('recompute', recompute)

    for key, data in VARIETIES.items():
        item = data['item']
        lore = data['lore'] + ['Stacks with different Karak drinks; same drink refreshes its timer.']
        emit(prefix + 'horizon/item/' + item.split(':', 1)[1] + '.json', {
            'template': 'minecraft:potion', 'max_stack_size': 16,
            'components': {'minecraft:item_name': data['name'], 'minecraft:item_model': item,
                'minecraft:lore': [{'text': line, 'color': 'gray', 'italic': False} for line in lore],
                'minecraft:consumable': {'consume_seconds': 1.6, 'animation': 'drink',
                    'sound': 'minecraft:entity.generic.drink', 'has_consume_particles': False,
                    'on_consume_effects': []},
                '!minecraft:potion_contents': {}, '!minecraft:use_remainder': {}}})
        lines = [f'execute unless entity @s[tag={READY}] run function karak_house:powers/init_player',
                 f'scoreboard players set @s {data["timer"]} {data["duration"]}',
                 f'scoreboard players set @s karak_refresh {data["number"]}',
                 'scoreboard players set @s karak_dirty 1', 'scoreboard players set @s karak_died 0']
        if key == 'milkshake':
            lines += ['function karak_house:powers/clear_harmful']
        else:
            # Keep the explicit normal-descent override on other new Karak
            # drinks. Milkshake's newer harmful-only rule preserves beneficials.
            lines += ['effect clear @s minecraft:slow_falling']
        lines += ['function karak_house:powers/recompute',
                  'advancement revoke @s only karak_house:powers/' + data['advancement']]
        function(data['start'], lines)
        consume_hook(data['advancement'], item, data['start'])

    clear = [f'scoreboard players set @s {v["timer"]} 0' for v in VARIETIES.values()]
    for effect, alias in ALIASES.items():
        clear += [f'execute if score @s karak_p_{alias} matches 1.. run effect clear @s minecraft:{effect}',
                  f'scoreboard players set @s karak_p_{alias} 0', f'scoreboard players set @s karak_l_{alias} 0']
    clear += ['function karak_house:powers/remove_fall', f'tag @s remove {DRINKER}',
              f'tag @s add {READY}', 'scoreboard players set @s karak_dirty 0',
              'scoreboard players set @s karak_refresh 0', 'scoreboard players set @s karak_died 0']
    function('clear', clear)
    function('milk', ['function karak_house:powers/clear',
                      'advancement revoke @s only karak_house:powers/drank_milk'])
    player_tick = [f'execute unless entity @s[tag={READY}] run function karak_house:powers/init_player',
                   'execute if score @s karak_died matches 1.. run function karak_house:powers/clear']
    player_tick += [f'execute if score @s karak_l_{alias} matches 1.. unless predicate karak_house:powers/present/{effect} run scoreboard players set @s karak_dirty 1'
                    for effect, alias in ALIASES.items()]
    player_tick += ['execute if score @s karak_dirty matches 1.. run function karak_house:powers/recompute',
                   'function karak_house:powers/update_no_fall',
                   'execute if score @s karak_t_milk matches 1.. run function karak_house:powers/protect_tick',
                   'advancement revoke @s only karak_house:powers/player_tick']
    function('player_tick', player_tick)
    emit(prefix + 'advancement/powers/player_tick.json', {
        'criteria': {'tick': {'trigger': 'minecraft:tick'}},
        'rewards': {'function': 'karak_house:powers/player_tick'}})
    consume_hook('drank_milk', 'minecraft:milk_bucket', 'milk')
    return written
