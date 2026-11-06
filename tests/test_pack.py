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
            self.assertEqual(f'minecraft:village/{style}/houses',x['horizon:add_to'])
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
            self.assertEqual(0,jigs[0]['pos'][2]) # road attachment begins continuous floor at front edge
    def test_daily_uses_persisted_monotonic_day(self):
        f=(ROOT/'data/karak_house/function/tick.mcfunction').read_text()
        self.assertIn('time of minecraft:overworld query day repetition',f)
        self.assertIn('karak_day < #today karak_sys',f)
    def test_giveaway_requires_real_talk_and_seller_in_crosshair(self):
        f=(ROOT/'data/karak_house/function/tick.mcfunction').read_text()
        self.assertIn('scores={karak_talk=1..}',f)
        self.assertIn('if predicate karak_house:looking_at_seller',f)
        self.assertIn('karak_talk 0',f)
    def test_effects(self):
        x=json.loads((ROOT/'data/karak_house/horizon/item/karak_tea.json').read_text())
        effects=x['components']['minecraft:consumable']['on_consume_effects'][0]['effects']
        self.assertEqual(7,len(effects));self.assertTrue(all(e['duration']==6000 for e in effects))
if __name__=='__main__':unittest.main()
