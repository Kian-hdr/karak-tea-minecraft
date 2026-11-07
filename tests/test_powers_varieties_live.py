"""Opt-in six-variety additive stacking and independent lifetime acceptance."""
import json
from pathlib import Path
import sys
import unittest
import test_powers_live as support
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from powers import VARIETIES, combined_levels


@unittest.skipUnless(support.CTL and support.SOCKET == '/tmp/karak-powers.sock', 'requires the dedicated powers fixture socket')
class KarakStackingLive(unittest.TestCase):
    ctl = support.PowersLive.ctl
    cmd = support.PowersLive.cmd
    score = support.PowersLive.score
    attribute = support.PowersLive.attribute
    drink = support.PowersLive.drink

    @classmethod
    def setUpClass(cls): cls.events = []
    @classmethod
    def tearDownClass(cls):
        out = ROOT / 'evidence/private/powers/Stacking_Live_Qualification.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cls.events, indent=2) + '\n')

    def bundle(self, active, ordinary=.75):
        state = self.ctl('state')
        self.assertEqual(combined_levels(active), {e['id']: e['amplifier'] + 1 for e in state['player']['effects']})
        self.assertEqual(0 if any(VARIETIES[k]['no_fall'] for k in active) else ordinary,
                         self.attribute('fall_damage_multiplier'))
        self.assertEqual(.08, self.attribute('gravity'))

    def timers(self): return {k: self.score('@s', v['timer']) for k, v in VARIETIES.items()}

    def test_independent_stacking_refresh_expiry_milk_and_death(self):
        self.assertEqual('Powers_Qualification', self.ctl('state')['world'])
        self.cmd('scoreboard objectives add karak_probe dummy')
        self.cmd('function karak_house:powers/clear')
        self.cmd('effect clear @s'); self.cmd('clear @s')
        self.cmd('attribute @s minecraft:fall_damage_multiplier modifier remove karak_house:test_other')
        self.cmd('attribute @s minecraft:fall_damage_multiplier modifier add karak_house:test_other -0.25 add_multiplied_total')
        active = []
        for key in ['regular', 'iced', 'decaf', 'pro_max', 'protein_shake', 'milkshake']:
            self.drink(VARIETIES[key]['item']); active.append(key); self.bundle(active)
            remaining = self.score('@s', VARIETIES[key]['timer'])
            self.assertGreater(remaining, VARIETIES[key]['duration'] - 100)
        self.events.append({'verified': 'all_six_once_maximum_levels', 'levels': combined_levels(active)})
        before = self.timers()
        self.drink(VARIETIES['regular']['item']); self.bundle(active)
        after = self.timers()
        self.assertGreater(after['regular'], before['regular'])
        for key in set(VARIETIES) - {'regular'}:
            self.assertLessEqual(after[key], before[key]); self.assertGreater(after[key], before[key] - 100)
        self.events.append({'verified': 'same_variety_no_multiplication_only_own_refresh', 'before': before, 'after': after})

        for key in ['regular', 'pro_max', 'protein_shake', 'iced', 'decaf']:
            self.cmd(f"scoreboard players set @s {VARIETIES[key]['timer']} 1")
            self.ctl('wait', 5); active.remove(key); self.bundle(active)
            self.assertEqual(0, self.score('@s', VARIETIES[key]['timer']))
            self.events.append({'verified_independent_expiry': key, 'remaining': active.copy()})
        self.assertGreater(self.score('@s', VARIETIES['milkshake']['timer']), 0)
        self.drink('minecraft:milk_bucket'); self.bundle([])
        self.assertTrue(all(v == 0 for v in self.timers().values()))

        self.drink(VARIETIES['regular']['item']); self.drink(VARIETIES['pro_max']['item'])
        self.bundle(['regular', 'pro_max'])
        self.cmd('execute store result score #natural_start karak_probe run time query gametime')
        self.cmd('tick sprint 6050')
        for _ in range(100):
            self.ctl('wait', 10)
            if self.score('@s', VARIETIES['regular']['timer']) == 0: break
        else: self.fail('Regular did not independently expire after 6000 server ticks')
        self.bundle(['pro_max'])
        remaining = self.score('@s', VARIETIES['pro_max']['timer'])
        self.assertGreater(remaining, 29000)
        self.events.append({'verified': 'natural_short_expiry_preserved_long_source', 'pro_remaining': remaining})
        self.cmd(f'tick sprint {remaining + 50}')
        for _ in range(120):
            self.ctl('wait', 10)
            if self.score('@s', VARIETIES['pro_max']['timer']) == 0: break
        else: self.fail('Pro Max did not expire at its independent deadline')
        self.bundle([])
        self.cmd('execute store result score #natural_end karak_probe run time query gametime')
        elapsed = self.score('#natural_end', 'karak_probe') - self.score('#natural_start', 'karak_probe')
        self.assertGreaterEqual(elapsed, 36000)
        self.events.append({'verified': 'natural_long_expiry', 'server_ticks_elapsed': elapsed})

        self.cmd('attribute @s minecraft:fall_damage_multiplier modifier remove karak_house:test_other')
        for data in VARIETIES.values(): self.cmd(f"scoreboard players set @s {data['timer']} 1000")
        self.cmd('scoreboard players set @s karak_dirty 1'); self.ctl('wait', 5)
        self.bundle(list(VARIETIES), 1)
        self.cmd('kill @s'); self.ctl('wait', 25); self.ctl('respawn'); self.ctl('wait', 10)
        self.bundle([], 1); self.assertTrue(all(v == 0 for v in self.timers().values()))
        self.cmd('tp @s 0.5 71 0.5'); self.cmd('clear @s'); self.ctl('save')


if __name__ == '__main__': unittest.main()
