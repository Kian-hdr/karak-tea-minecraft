"""Generation and data invariants, complemented by real game acceptance tests."""
import json, unittest
from pathlib import Path
import nbtlib
ROOT = Path(__file__).resolve().parents[1] / 'pack'
STYLES=['plains','desert','savanna','taiga','snowy']
class PackTests(unittest.TestCase):
    def test_single_capped_direct_shop_per_village_style(self):
        paths=list((ROOT/'data/karak_house/worldgen/template_pool/additions').glob('*.json'))
        self.assertEqual(5,len(paths))
        for style in STYLES:
            x=json.loads((ROOT/f'data/karak_house/worldgen/template_pool/additions/{style}.json').read_text())
            targets=x['horizon:add_to']
            self.assertIn(f'minecraft:village/{style}/houses',targets)
            self.assertIn(f'minecraft:village/{style}/zombie/houses',targets)
            self.assertEqual(1,len(x['elements']))
            e=x['elements'][0]['element'];self.assertEqual('lithostitched:guaranteed',e['element_type'])
            self.assertEqual(1,e['count'])
            self.assertEqual(f'karak_house:village/karak_house_{style}',e['delegate']['location'])
    def test_shops_have_one_seller_and_no_outgoing_shop_connector(self):
        for style in STYLES:
            x=nbtlib.load(ROOT/f'data/karak_house/structure/village/karak_house_{style}.nbt')
            sellers=[e for e in x['entities'] if e['nbt']['id']=='minecraft:villager']
            self.assertEqual(1,len(sellers))
            o=sellers[0]['nbt']['Offers']['Recipes'];self.assertEqual(1,len(o))
            self.assertEqual('minecraft:emerald',o[0]['buy']['id']);self.assertEqual(1,o[0]['buy']['count'])
            self.assertEqual(1,o[0]['sell']['count']);self.assertEqual(0,o[0]['priceMultiplier'])
            jigs=[b for b in x['blocks'] if x['palette'][b['state']]['id']=='minecraft:jigsaw']
            self.assertEqual(1,len(jigs));self.assertEqual('minecraft:empty',jigs[0]['nbt']['pool'])
            self.assertEqual(1,jigs[0]['pos'][1]);self.assertEqual('minecraft:air',jigs[0]['nbt']['final_state'])
            self.assertEqual(0,jigs[0]['pos'][2]) # road attachment begins continuous floor at front edge
    def test_reviewed_facade_and_furniture_across_all_styles(self):
        for style in STYLES:
            x=nbtlib.load(ROOT/f'data/karak_house/structure/village/karak_house_{style}.nbt')
            blocks={tuple(map(int,b['pos'])):x['palette'][b['state']] for b in x['blocks']}
            w,d=int(x['size'][0]),int(x['size'][2]);mid=w//2
            glass=blocks[(5,5,5)]['id']
            self.assertEqual(glass,blocks[(mid,3,5)]['id'])
            self.assertTrue(str(blocks[(5,4,5)]['id']).endswith('_planks'))
            self.assertEqual('south',blocks[(mid,1,5)]['properties']['facing'])
            self.assertEqual('right',blocks[(mid,1,5)]['properties']['hinge'])
            self.assertEqual('left',blocks[(mid+1,1,5)]['properties']['hinge'])
            self.assertEqual('north',blocks[(2,1,1)]['properties']['facing'])
            self.assertEqual('south',blocks[(2,1,3)]['properties']['facing'])
            self.assertTrue(all('fence' not in str(blocks[(xx,2,d-4)]['id']) for xx in range(2,w-1)))
            self.assertTrue(str(blocks[(3,2,7)]['id']).endswith('_pressure_plate'))
            self.assertTrue(str(blocks[(w-4,2,7)]['id']).endswith('_pressure_plate'))
            labels=[e for e in x['entities'] if e['nbt']['id']=='minecraft:text_display']
            self.assertEqual({'KARAK','HOUSE'},{str(e['nbt']['text']) for e in labels})
    def test_no_carpets_and_no_unsupported_pots_or_wall_signs(self):
        for style in STYLES:
            x=nbtlib.load(ROOT/f'data/karak_house/structure/village/karak_house_{style}.nbt')
            blocks={tuple(map(int,b['pos'])):x['palette'][b['state']] for b in x['blocks']}
            for (xx,yy,zz),state in blocks.items():
                name=str(state['id'])
                self.assertFalse(name.endswith('_carpet'))
                if name=='minecraft:flower_pot' or name.startswith('minecraft:potted_'):
                    below=blocks[(xx,yy-1,zz)]
                    self.assertNotIn(str(below['id']),['minecraft:air','minecraft:chain','minecraft:flower_pot'])
                    self.assertFalse(str(below['id']).startswith('minecraft:potted_'))
                    if str(below['id']).endswith('_slab'):
                        self.assertIn(str(below['properties']['type']),['top','double'])
                if name.endswith('_wall_sign'):
                    self.assertNotEqual('minecraft:air',blocks[(xx,yy,zz+1)]['id'])
    def test_daily_uses_persisted_monotonic_day(self):
        f=(ROOT/'data/karak_house/function/tick.mcfunction').read_text()
        self.assertIn('time of minecraft:overworld query day repetition',f)
        self.assertIn('karak_day < #today karak_sys',f)
    def test_effects(self):
        x=json.loads((ROOT/'data/karak_house/horizon/item/karak_tea.json').read_text())
        effects=x['components']['minecraft:consumable']['on_consume_effects'][0]['effects']
        self.assertEqual(7,len(effects));self.assertTrue(all(e['duration']==6000 for e in effects))
if __name__=='__main__':unittest.main()
