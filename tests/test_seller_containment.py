"""Stationed sellers must retain normal AI and remain within lectern work range."""
import importlib.util
from pathlib import Path
import sys
import unittest
import nbtlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
from gameplay import write_gameplay

class SellerContainmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_pack=build.PACK
        build.PACK=ROOT/'.test/containment/generated'
        try:build.structures()
        finally:build.PACK=cls.original_pack

    def test_all_five_sellers_cannot_walk_or_jump_but_keep_normal_ai(self):
        for style in build.THEMES:
            with self.subTest(style=style):
                x=nbtlib.load(ROOT/f'.test/containment/generated/data/karak_house/structure/village/karak_house_{style}.nbt')
                seller=next(e['nbt'] for e in x['entities'] if e['nbt']['id']=='minecraft:villager')
                attrs={str(a['id']):float(a['base']) for a in seller.get('attributes',[])}
                self.assertEqual(0,attrs.get('minecraft:movement_speed'))
                self.assertFalse(seller.get('NoAI',False))
                self.assertEqual(16,int(seller['Offers']['Recipes'][0]['maxUses']))
                lectern=next(b for b in x['blocks'] if x['palette'][b['state']]['id']=='minecraft:lectern')
                pos=[float(v) for v in seller['Pos']]
                distance=sum((float(lectern['pos'][i])+0.5-pos[i])**2 for i in range(3))**0.5
                self.assertLess(distance,1.73)

    def test_explicit_repair_operates_on_one_selected_seller_and_supplied_station(self):
        files={};write_gameplay(files.__setitem__)
        repair=files['data/karak_house/function/station_seller.mcfunction']
        self.assertIn('attribute @s minecraft:movement_speed base set 0',repair)
        self.assertIn('attribute @s minecraft:jump_strength base set 0',repair)
        self.assertIn('tp @s ~ ~ ~',repair)
        self.assertNotIn('NoAI',repair)
        self.assertNotIn('Offers',repair)
        tick=files['data/karak_house/function/tick.mcfunction']
        self.assertIn('run function karak_house:stations/harden',tick)
        from stations import write_stations
        write_stations(files.__setitem__)
        self.assertIn('attribute @s minecraft:jump_strength base set 0',files['data/karak_house/function/stations/harden.mcfunction'])
        self.assertLess(repair.index('data merge entity'),repair.index('attribute @s minecraft:jump_strength'))

if __name__=='__main__':unittest.main()
