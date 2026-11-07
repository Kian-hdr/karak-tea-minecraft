"""Current six-variety stacking invariants, complemented by real engine tests."""
import sys
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from powers import ATTRIBUTE, MODIFIER, VARIETIES, combined_levels, reconcile_owned_generated, write_powers


class PowerDefinitions(unittest.TestCase):
    def setUp(self):
        self.files = {}
        write_powers(self.files.__setitem__)

    def test_six_items_have_clear_lore_and_no_duplicate_native_bonuses(self):
        self.assertEqual(6, len(VARIETIES))
        for key, data in VARIETIES.items():
            item = self.files['data/karak_house/horizon/item/' + data['item'].split(':')[1] + '.json']
            comp = item['components']
            self.assertEqual(data['item'], comp['minecraft:item_model'])
            self.assertEqual([], comp['minecraft:consumable']['on_consume_effects'])
            self.assertIn('Stacks with different Karak drinks', comp['minecraft:lore'][-1]['text'])
            self.assertEqual(36000 if key == 'pro_max' else 6000, data['duration'])

    def test_levels_add_without_caps_and_binary_effects_or(self):
        self.assertEqual({'strength': 17, 'speed': 7, 'jump_boost': 7, 'resistance': 5,
                          'regeneration': 4, 'fire_resistance': 1, 'water_breathing': 1,
                          'night_vision': 1}, combined_levels(VARIETIES))
        self.assertEqual(10, combined_levels(['regular', 'pro_max'])['strength'])
        self.assertEqual({}, combined_levels(['milkshake']))
        self.assertEqual({'strength': 7}, combined_levels(['protein_shake']))

    def test_refresh_changes_only_own_timer_and_never_clears_other_drinks(self):
        timers = {v['timer'] for v in VARIETIES.values()}
        for data in VARIETIES.values():
            start = self.files['data/karak_house/function/powers/' + data['start'] + '.mcfunction']
            self.assertIn(f"set @s {data['timer']} {data['duration']}", start)
            self.assertNotIn('function karak_house:powers/clear\n', start)
            for other in timers - {data['timer']}:
                self.assertNotIn('set @s ' + other + ' ', start)

    def test_server_tick_independently_expires_each_timer(self):
        tick = self.files['data/karak_house/function/powers/tick.mcfunction']
        for data in VARIETIES.values():
            self.assertIn(f"remove @a[scores={{{data['timer']}=1..}}] {data['timer']} 1", tick)
            self.assertIn(f"@a[scores={{{data['timer']}=1}}]", tick)
        self.assertNotIn('attribute ', tick)
        self.assertNotIn('effect ', tick)

    def test_changed_level_is_cleared_then_macro_reapplied(self):
        apply = self.files['data/karak_house/function/powers/apply/strength.mcfunction']
        self.assertTrue(apply.startswith('effect clear @s minecraft:strength\n'))
        macro = self.files['data/karak_house/function/powers/macro/strength.mcfunction']
        self.assertEqual('$effect give @s minecraft:strength $(seconds) $(amplifier) false\n', macro)
        fall = self.files['data/karak_house/function/powers/reapply.mcfunction']
        self.assertIn(f'{ATTRIBUTE} modifier add {MODIFIER} -1 add_multiplied_total', fall)
        self.assertNotIn('gravity', fall)
        self.assertNotIn('base set', fall)

    def test_milkshake_is_harmful_only_and_legacy_timer_is_not_reset(self):
        start = self.files['data/karak_house/function/powers/start_milkshake.mcfunction']
        self.assertIn('clear_harmful', start)
        self.assertNotIn('effect clear @s\n', start)
        self.assertNotIn('slow_falling', start)
        harmful = self.files['data/karak_house/function/powers/clear_harmful.mcfunction']
        self.assertNotIn('regeneration', harmful)
        self.assertNotIn('night_vision', harmful)
        self.assertNotIn('slow_falling', harmful)
        migrate = self.files['data/karak_house/function/powers/migrate_regular.mcfunction']
        self.assertIn('active_effects[{id:"minecraft:fire_resistance"}].duration', migrate)
        self.assertNotIn('karak_t_reg 6000', migrate)

    def test_repeat_build_prunes_stale_hooks_and_has_one_hook_per_item(self):
        hooks = [v for k, v in self.files.items() if '/advancement/powers/' in k
                 and v['criteria'].get('consume', {}).get('trigger') == 'minecraft:consume_item']
        for item in [v['item'] for v in VARIETIES.values()] + ['minecraft:milk_bucket']:
            self.assertEqual(1, sum(h['criteria']['consume']['conditions']['item']['items'] == [item] for h in hooks))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stale = root / 'data/karak_house/advancement/powers/old_duplicate.json'
            stale.parent.mkdir(parents=True)
            stale.write_text('{}')
            outside = root / 'data/karak_house/advancement/user.json'
            outside.write_text('preserve')
            def writer(path, value):
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(value if isinstance(value, str) else json.dumps(value, indent=2) + '\n')
            emitted = write_powers(writer)
            self.assertEqual(['data/karak_house/advancement/powers/old_duplicate.json'], reconcile_owned_generated(root, emitted))
            before = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in emitted}
            self.assertEqual(emitted, write_powers(writer))
            self.assertEqual([], reconcile_owned_generated(root, emitted))
            self.assertEqual(before, {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in emitted})
            self.assertEqual('preserve', outside.read_text())


if __name__ == '__main__':
    unittest.main()
