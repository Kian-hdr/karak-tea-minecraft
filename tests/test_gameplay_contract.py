"""Cross-file gameplay contracts; live interaction tests are opt-in separately."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from gameplay import write_gameplay

class GameplayContractTests(unittest.TestCase):
    def setUp(self):
        self.files={}
        write_gameplay(self.files.__setitem__)

    def test_player_context_polling_is_repeatable_and_clears_unmatched_events(self):
        adv=self.files['data/karak_house/advancement/player_tick.json']
        self.assertEqual('minecraft:tick',adv['criteria']['tick']['trigger'])
        reward=adv['rewards']['function'].split(':')[1]
        source=self.files[f'data/karak_house/function/{reward}.mcfunction']
        self.assertIn('if score @s karak_talk matches 1..',source)
        self.assertIn('scoreboard players set @s karak_talk 0',source)
        self.assertIn('advancement revoke @s only karak_house:player_tick',source)
        server_tick=self.files['data/karak_house/function/tick.mcfunction']
        self.assertNotIn('karak_talk',server_tick)

    def test_target_scan_keeps_the_player_as_executor_until_delivery(self):
        scan=self.files['data/karak_house/function/check_target.mcfunction']
        self.assertIn('karak_unchecked,sort=nearest,limit=1',scan)
        self.assertIn('if predicate karak_house:looking_at_target',scan)
        self.assertIn('remove karak_unchecked',scan)
        self.assertIn('remove karak_target',scan)
        predicate=self.files['data/karak_house/predicate/looking_at_target.json']
        self.assertIn('karak_target',json.dumps(predicate))
        giveaway=self.files['data/karak_house/function/giveaway.mcfunction']
        self.assertIn('give @s karak_house:karak_tea 1',giveaway)
        self.assertLess(giveaway.index('karak_free 0'),giveaway.index('give @s'))
        for name in ['interact','check_target','claim_target','giveaway']:
            self.assertNotIn('execute as ',self.files[f'data/karak_house/function/{name}.mcfunction'])

    def test_independent_daily_roll_is_persisted_before_it_is_used(self):
        daily=self.files['data/karak_house/function/new_day.mcfunction']
        self.assertLess(daily.index('karak_day = #today'),daily.index('random value 1..10'))
        self.assertIn('unless score @s karak_free matches 1',daily)
        tick=self.files['data/karak_house/function/tick.mcfunction']
        self.assertIn('karak_day < #today',tick)
        self.assertNotIn('karak_day = #today',tick)

    def test_effect_identity_duration_and_amplifier(self):
        item=json.loads((ROOT/'pack/data/karak_house/horizon/item/karak_tea.json').read_text())
        effects=item['components']['minecraft:consumable']['on_consume_effects'][0]['effects']
        expected={'strength':3,'speed':2,'jump_boost':2,'resistance':1,'regeneration':0,'fire_resistance':0,'slow_falling':0}
        self.assertEqual({f'minecraft:{k}':v for k,v in expected.items()},{e['id']:e['amplifier'] for e in effects})
        self.assertTrue(all(e['duration']==6000 for e in effects))

if __name__=='__main__':unittest.main()
