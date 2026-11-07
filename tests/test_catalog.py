import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog import CATALOG, offer, write_catalog
from cup_model import write_cup_model
class CatalogTests(unittest.TestCase):
    def test_prices_and_single_cup_outputs(self):
        self.assertEqual([1,1,1,2,3,8],[offer(item)['buy']['count'] for item,_,_ in CATALOG])
        for item,_,_ in CATALOG:
            o=offer(item)
            self.assertEqual('minecraft:emerald',o['buy']['id'])
            self.assertEqual(1,o['sell']['count']);self.assertNotIn('buyB',o)
            self.assertEqual(0,o['xp']);self.assertEqual(0,o['priceMultiplier'])
    def test_upgrade_checks_each_recipe_before_appending(self):
        out={};write_catalog(lambda k,v:out.__setitem__(k,v))
        f=out['data/karak_house/function/catalog/upgrade_seller.mcfunction']
        for item,_,_ in CATALOG:
            self.assertIn(f'execute unless data entity @s Offers.Recipes[{{sell:{{id:"karak_house:{item}"}}}}]',f)
        self.assertEqual(6,f.count('append value'))
    def test_each_catalog_item_has_a_distinct_model_and_sleeve(self):
        out={};write_cup_model(lambda k,v:out.__setitem__(k,v))
        textures=[]
        for item,_,_ in CATALOG:
            m=out[f'assets/karak_house/models/item/{item}.json'];textures.append(m['textures']['sleeve'])
            self.assertEqual('karak_house:item/'+item,out[f'assets/karak_house/items/{item}.json']['model']['model'])
        self.assertEqual(6,len(set(textures)))
        normal=out['assets/karak_house/models/item/karak_tea.json']['elements']
        pro=out['assets/karak_house/models/item/karak_pro_max.json']['elements']
        self.assertGreater(max(e['to'][1] for e in pro),max(e['to'][1] for e in normal)*1.2)
if __name__=='__main__':unittest.main()
