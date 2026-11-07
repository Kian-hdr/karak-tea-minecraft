"""Opt-in upgrade of old regular into a preserved independent contribution."""
import json
from pathlib import Path
import sys
import unittest
import test_powers_live as support
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from powers import EFFECTS, combined_levels


@unittest.skipUnless(support.CTL and support.SOCKET == '/tmp/karak-powers.sock', 'requires the dedicated powers fixture socket')
class LegacyKarakLive(unittest.TestCase):
    ctl = support.PowersLive.ctl
    cmd = support.PowersLive.cmd
    score = support.PowersLive.score
    attribute = support.PowersLive.attribute
    drink = support.PowersLive.drink
    @classmethod
    def setUpClass(cls): cls.events = []
    @classmethod
    def tearDownClass(cls):
        out = ROOT / 'evidence/private/powers/Legacy_Independent_Timer_Live.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cls.events, indent=2) + '\n')

    def test_old_regular_preserves_remaining_time_and_stacks_with_iced(self):
        self.assertEqual('Powers_Qualification', self.ctl('state')['world'])
        self.cmd('scoreboard objectives add karak_probe dummy')
        for slow in [True, False]:
            self.cmd('function karak_house:powers/clear'); self.cmd('effect clear @s')
            for effect, amplifier in EFFECTS + ([('slow_falling', 0)] if slow else []):
                self.cmd(f'effect give @s {effect} 300 {amplifier}')
            self.ctl('wait', 30)
            state = self.ctl('state')
            before = next(e['duration_ticks'] for e in state['player']['effects'] if e['id'] == 'fire_resistance')
            self.cmd('tag @s remove karak_stack_ready'); self.ctl('wait', 4)
            imported = self.score('@s', 'karak_t_reg')
            self.assertGreater(imported, before - 40); self.assertLessEqual(imported, before)
            self.assertEqual(0, self.attribute('fall_damage_multiplier'))
            self.assertNotIn('slow_falling', [e['id'] for e in self.ctl('state')['player']['effects']])
            self.drink('karak_house:iced_karak')
            self.assertLess(self.score('@s', 'karak_t_reg'), imported)
            self.assertEqual(combined_levels(['regular', 'iced']),
                             {e['id']: e['amplifier'] + 1 for e in self.ctl('state')['player']['effects']})
        self.drink('minecraft:milk_bucket'); self.cmd('clear @s'); self.ctl('save')


if __name__ == '__main__': unittest.main()
