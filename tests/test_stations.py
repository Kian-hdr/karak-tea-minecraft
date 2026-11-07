"""Respawn station invariants independent of the runtime integration fixture."""
import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stations import seller_nbt,anchor_nbt,write_stations,STYLES
from gameplay import write_gameplay
from catalog import CATALOG

class StationTests(unittest.TestCase):
 def setUp(self):
  self.files={};write_stations(self.files.__setitem__);write_gameplay(self.files.__setitem__)
 def fn(self,name):return self.files['data/karak_house/function/stations/'+name+'.mcfunction']
 def test_all_styles_have_killable_durable_vendor_and_noncolliding_saved_anchor(self):
  for style in STYLES:
   seller=seller_nbt(style,[6.5,1.,10.5]);anchor=anchor_nbt(style,[6.5,1.,10.5])
   self.assertEqual(200.,seller['Health']);self.assertNotIn('Invulnerable',seller);self.assertNotIn('NoAI',seller)
   self.assertEqual(len(CATALOG),len(seller['Offers']['Recipes']))
   self.assertTrue(all(x['maxUses']==16 and x['priceMultiplier']==0 for x in seller['Offers']['Recipes']))
   self.assertEqual('minecraft:marker',anchor['id']);self.assertEqual(seller['Pos'],anchor['Pos'])
   self.assertIn('karak_style_'+style,anchor['Tags'])
 def test_damage_is_not_healed_each_tick(self):
  self.assertNotIn('Health:',self.fn('harden'));self.assertIn('minecraft:armor base set 12',self.fn('harden'))
  self.assertIn('minecraft:knockback_resistance base set 1',self.fn('harden'))
 def test_claim_is_committed_to_station_before_item_delivery(self):
  gift=self.files['data/karak_house/function/giveaway.mcfunction']
  self.assertLess(gift.index('stations/commit_claim'),gift.index('give @s'))
  self.assertIn('unless score',self.fn('commit_claim'))
  self.assertIn('karak_free 0',self.fn('commit_claim'))
 def test_respawn_wait_and_saved_state_restoration(self):
  self.assertIn('karak_wait matches 100..',self.fn('check'))
  for obj in ['karak_day','karak_free','karak_sid']:self.assertIn(obj,self.fn('restore'))
  self.assertNotIn('random',self.fn('respawn'));self.assertNotIn('random',self.fn('restore'))
  self.assertIn('unless score #next_station',self.fn('load'))
  for style in STYLES:
   install=self.fn('install_'+style)
   self.assertLess(install.index('run return 0'),install.index('summon'))
   self.assertIn('karak_style_'+style,self.fn('spawn_'+style))

if __name__=='__main__':unittest.main()
