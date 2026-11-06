"""Opt-in acceptance test against an isolated, already-running Horizon fixture.

Set KARAK_GAMEPLAY_SOCKET to a disposable test world's control socket. This
changes that world. Never point it at a player's world. Results stay in the
private evidence tree; no screenshots or personal paths are published.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOCKET = os.environ.get('KARAK_GAMEPLAY_SOCKET')
CTL = os.environ.get('HORIZON_CTL')

@unittest.skipUnless(SOCKET and CTL, 'requires explicit isolated-world control socket')
class GameplayLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events=[]

    @classmethod
    def tearDownClass(cls):
        out=ROOT/'evidence/private/gameplay/live_results.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(cls.events,indent=2)+'\n')

    def ctl(self,*args):
        p=subprocess.run([CTL,'--socket',SOCKET,*map(str,args)],capture_output=True,text=True,timeout=70)
        self.assertEqual(p.returncode,0,p.stderr or p.stdout)
        data=json.loads(p.stdout); self.events.append({'command':list(args),'result':data})
        self.assertNotIn('error',data)
        return data

    def cmd(self,s): return self.ctl('command',s)
    def count(self,item):return self.ctl('inventory')['counts'].get(item,0)
    def score(self,target,obj):
        text=' '.join(self.cmd(f'scoreboard players get {target} {obj}')['chat'])
        return int(re.search(r' has (-?\d+) \[',text).group(1))
    def close(self):self.ctl('close');self.ctl('wait',3)
    def click(self):
        self.close();self.ctl('select','9');self.ctl('use-item');self.ctl('wait',5)

    def test_01_click_claim_targets_and_persistence(self):
        self.close();self.cmd('gamemode creative');self.cmd('time pause')
        self.cmd('kill @e[tag=karak_seller]');self.cmd('clear @s')
        self.cmd('fill -5 69 -5 5 69 5 stone');self.cmd('tp @s 0 70 0')
        for label,x,z in [('test_a',0,3),('test_b',2,2)]:
            self.cmd('summon villager '+f'{x} 70 {z} '+
                '{Tags:["karak_seller","'+label+'"],NoAI:1b,PersistenceRequired:1b,'
                'VillagerData:{profession:"minecraft:cleric",level:2,type:"minecraft:plains"},Xp:10,'
                'Offers:{Recipes:[{buy:{id:"minecraft:emerald",count:1},sell:{id:"karak_house:karak_tea",count:1},maxUses:16,uses:0,xp:0,priceMultiplier:0.0f}]}}')
        self.ctl('wait',4);self.cmd('scoreboard players set @e[tag=karak_seller] karak_free 1')
        self.ctl('look','0','0');self.ctl('wait',5)
        self.assertEqual(self.count('karak_house:karak_tea'),0,'looking alone must not claim')
        self.click()
        self.assertEqual(self.count('karak_house:karak_tea'),1)
        self.assertEqual(self.score('@e[tag=test_a,limit=1]','karak_free'),0)
        self.assertEqual(self.score('@e[tag=test_b,limit=1]','karak_free'),1)
        self.click();self.assertEqual(self.count('karak_house:karak_tea'),1)
        self.close();self.cmd('reload');self.ctl('wait',4);self.click()
        self.assertEqual(self.count('karak_house:karak_tea'),1,'reload must not reset claim')
        self.close();self.ctl('save');self.cmd('tp @s 1000 90 1000');self.ctl('wait',40)
        self.cmd('tp @s 0 70 0');self.ctl('look','0','0');self.ctl('wait',40);self.click()
        self.assertEqual(self.count('karak_house:karak_tea'),1,'chunk unload must not reset claim')
        self.close();self.ctl('look-at',2.5,71.4,2.5);self.click()
        self.assertEqual(self.count('karak_house:karak_tea'),2,'other seller has independent claim')
        self.assertEqual(self.score('@e[tag=test_b,limit=1]','karak_free'),0)
        day=self.score('@e[tag=test_a,limit=1]','karak_day')
        self.cmd('time set '+str((day+1)*24000));self.ctl('wait',5)
        self.assertEqual(self.score('@e[tag=test_a,limit=1]','karak_day'),day+1)
        before=[self.score(f'@e[tag={label},limit=1]','karak_free') for label in ['test_a','test_b']]
        self.cmd('time set 0');self.ctl('wait',5)
        self.assertEqual(self.score('@e[tag=test_a,limit=1]','karak_day'),day+1)
        self.assertEqual([self.score(f'@e[tag={label},limit=1]','karak_free') for label in ['test_a','test_b']],before)

    def test_02_drink_refresh_milk_death(self):
        self.close();self.cmd('clear @s');self.cmd('effect clear @s');self.cmd('gamemode survival')
        self.cmd('give @s karak_house:karak_tea 3');self.ctl('wait',3);self.ctl('select','karak_house:karak_tea')
        self.ctl('look','180','-50');self.ctl('mouse','right','down');self.ctl('wait',35);self.ctl('mouse','right','up');self.ctl('wait',3)
        effects=self.ctl('state')['player']['effects']
        self.assertEqual(len(effects),7,effects)
        self.events.append({'verified':'drink_effects','effects':effects})
        self.ctl('wait',40);self.ctl('mouse','right','down');self.ctl('wait',35);self.ctl('mouse','right','up');self.ctl('wait',3)
        refreshed=self.ctl('state')['player']['effects'];self.assertEqual(len(refreshed),7)
        self.events.append({'verified':'refresh_effects','effects':refreshed})
        self.cmd('give @s milk_bucket');self.ctl('wait',3);self.ctl('select','milk_bucket');self.ctl('mouse','right','down');self.ctl('wait',35);self.ctl('mouse','right','up');self.ctl('wait',3)
        self.assertEqual(self.ctl('state')['player']['effects'],[])
        self.ctl('select','karak_house:karak_tea');self.ctl('mouse','right','down');self.ctl('wait',35);self.ctl('mouse','right','up');self.ctl('wait',3)
        self.assertEqual(len(self.ctl('state')['player']['effects']),7)
        self.cmd('kill @s');self.ctl('wait',25);self.ctl('respawn');self.ctl('wait',20)
        self.assertEqual(self.ctl('state')['player']['effects'],[])

if __name__=='__main__':unittest.main()
